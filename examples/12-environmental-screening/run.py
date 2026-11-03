"""Synthetic, preliminary environmental constraints screening.

Not a regulatory determination, field delineation, or certified assessment.
All area calculations require a projected CRS with metre units.
"""
from __future__ import annotations

import geopandas as gpd
from shapely.geometry import box

SQM_PER_ACRE = 4046.8564224


def screen(sites: gpd.GeoDataFrame, constraints: gpd.GeoDataFrame,
           coverage: gpd.GeoDataFrame) -> list[dict]:
    """Return one row per site and constraint type; never conflate missing coverage with zero overlap.

    Required columns: sites.site_id, constraints.constraint_type; all inputs must
    have the same projected metre CRS. Coverage must describe the spatial extent
    of *each* constraint type, including areas without mapped features.
    """
    for label, frame in (("sites", sites), ("constraints", constraints), ("coverage", coverage)):
        if frame.crs is None or not frame.crs.is_projected:
            raise ValueError(f"{label} must have a projected CRS")
        if frame.crs.axis_info and any(axis.unit_name.lower() not in ("metre", "meter", "metres", "meters")
                                       for axis in frame.crs.axis_info[:2]):
            raise ValueError(f"{label} must use metre units")
        if frame.geometry.isna().any() or frame.geometry.is_empty.any() or not frame.geometry.is_valid.all():
            raise ValueError(f"{label} contains null, empty, or invalid geometry")
    if sites.crs != constraints.crs or sites.crs != coverage.crs:
        raise ValueError("CRS mismatch: reproject and verify before screening")
    if sites.site_id.isna().any() or sites.site_id.duplicated().any():
        raise ValueError("site_id must be present and unique")
    if "constraint_type" not in constraints or "constraint_type" not in coverage:
        raise ValueError("constraint_type required in constraints and coverage")
    if constraints.constraint_type.isna().any() or coverage.constraint_type.isna().any():
        raise ValueError("constraint_type must not be null")

    rows = []
    types = sorted(set(constraints.constraint_type) | set(coverage.constraint_type))
    for site in sites.itertuples():
        site_area = site.geometry.area
        if site_area <= 0:
            raise ValueError("Site area must be positive")
        for kind in types:
            covered = coverage.loc[coverage.constraint_type == kind, "geometry"]
            # Partial source coverage is not evidence of a complete negative result.
            coverage_union = covered.union_all() if len(covered) else None
            fully_covered = bool(coverage_union is not None and coverage_union.covers(site.geometry))
            if not fully_covered:
                rows.append({"site_id": site.site_id, "constraint_type": kind,
                             "status": "no_source_coverage", "overlap_m2": None,
                             "overlap_acres": None, "pct_site": None})
                continue
            features = constraints.loc[constraints.constraint_type == kind, "geometry"]
            clipped = [geom.intersection(site.geometry) for geom in features if geom.intersects(site.geometry)]
            # Union avoids double counting duplicate or overlapping constraint features.
            overlap = gpd.GeoSeries(clipped, crs=sites.crs).union_all().area if clipped else 0.0
            rows.append({"site_id": site.site_id, "constraint_type": kind,
                         "status": "intersects" if overlap > 0 else "no_mapped_intersection",
                         "overlap_m2": overlap, "overlap_acres": overlap / SQM_PER_ACRE,
                         "pct_site": overlap / site_area * 100})
    return rows


def synthetic_demo() -> list[dict]:
    crs = "EPSG:32617"
    sites = gpd.GeoDataFrame({"site_id": ["SITE-1"]}, geometry=[box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame(
        {"constraint_type": ["wetland_inventory", "wetland_inventory", "flood_hazard"]},
        geometry=[box(500000, 3200000, 500050, 3200100),
                  box(500000, 3200000, 500050, 3200100),
                  box(500200, 3200000, 500300, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame(
        {"constraint_type": ["wetland_inventory", "flood_hazard", "soil_inventory"]},
        geometry=[box(499900, 3199900, 500200, 3200200),
                  box(499900, 3199900, 500200, 3200200),
                  box(500200, 3200000, 500300, 3200100)], crs=crs)
    return screen(sites, constraints, coverage)


if __name__ == "__main__":
    for result in synthetic_demo():
        print(result)
