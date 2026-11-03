"""Parcel-scale screening with explicit source coverage and boundary uncertainty.

Synthetic-only example. Parcel polygons are GIS representations, not surveyed
property lines. A fine display scale cannot improve underlying source accuracy.
"""
from __future__ import annotations

import geopandas as gpd

SQM_PER_ACRE = 4046.8564224


def parcel_screen(parcels: gpd.GeoDataFrame, constraints: gpd.GeoDataFrame,
                  coverage: gpd.GeoDataFrame) -> list[dict]:
    """Screen each parcel/type, reporting known overlap and unscreened area.

    All inputs must share a projected metre CRS. Coverage must explicitly
    describe valid source coverage for each constraint type. Unknown area
    is never counted as unconstrained land.
    """
    for name, frame, required in (
        ("parcels", parcels, ("parcel_id",)),
        ("constraints", constraints, ("constraint_type",)),
        ("coverage", coverage, ("constraint_type",)),
    ):
        if not all(column in frame.columns for column in required):
            raise ValueError(f"{name}: missing required columns")
        if frame.crs is None or not frame.crs.is_projected:
            raise ValueError(f"{name}: projected metre CRS required")
        axes = frame.crs.axis_info[:2]
        if len(axes) != 2 or any(axis.unit_name.lower() not in ("metre", "meter", "metres", "meters") for axis in axes):
            raise ValueError(f"{name}: metre units required")
        if frame.geometry.isna().any() or frame.geometry.is_empty.any() or not frame.geometry.is_valid.all():
            raise ValueError(f"{name}: invalid, empty or missing geometry")
        if not frame.geometry.geom_type.isin(("Polygon", "MultiPolygon")).all():
            raise ValueError(f"{name}: polygon geometries required")
    if parcels.crs != constraints.crs or parcels.crs != coverage.crs:
        raise ValueError("All layers must use the same projected metre CRS")
    if (parcels.parcel_id.isna().any() or parcels.parcel_id.duplicated().any()
            or not parcels.parcel_id.map(lambda value: isinstance(value, str) and bool(value.strip())).all()):
        raise ValueError("parcel_id must be a unique nonempty string")
    for frame in (constraints, coverage):
        if not frame.constraint_type.map(lambda value: isinstance(value, str) and bool(value.strip())).all():
            raise ValueError("constraint_type must be a nonempty string")

    types = sorted(set(constraints.constraint_type) | set(coverage.constraint_type))
    coverage_unions = {}
    constraint_unions = {}
    for kind in types:
        c = coverage.loc[coverage.constraint_type == kind, "geometry"]
        f = constraints.loc[constraints.constraint_type == kind, "geometry"]
        coverage_unions[kind] = c.union_all() if len(c) else None
        constraint_unions[kind] = f.union_all() if len(f) else None

    rows = []
    for parcel in parcels.itertuples():
        area = parcel.geometry.area
        if area <= 0:
            raise ValueError("Parcel polygon must have positive area")
        for kind in types:
            extent = coverage_unions[kind]
            covered = parcel.geometry.intersection(extent) if extent is not None else None
            covered_m2 = min(area, covered.area) if covered is not None else 0.0
            unknown_m2 = max(0.0, area - covered_m2)
            feature = constraint_unions[kind]
            known_overlap = (min(covered_m2, covered.intersection(feature).area)
                             if feature is not None and covered is not None else 0.0)
            # Boundary-touching features are not positive-area overlaps.
            if unknown_m2 > max(1e-6, area * 1e-9):
                status = "partial_source_coverage" if covered_m2 > 0 else "no_source_coverage"
            else:
                status = "intersects" if known_overlap > 0 else "no_mapped_intersection"
            rows.append({
                "parcel_id": parcel.parcel_id,
                "constraint_type": kind,
                "status": status,
                "parcel_m2": area,
                "parcel_acres": area / SQM_PER_ACRE,
                "covered_m2": covered_m2,
                "unknown_m2": unknown_m2,
                "known_overlap_m2": known_overlap,
                "known_overlap_acres": known_overlap / SQM_PER_ACRE,
                "known_overlap_pct_parcel": 100 * known_overlap / area,
                "coverage_pct_parcel": 100 * covered_m2 / area,
            })
    return rows
