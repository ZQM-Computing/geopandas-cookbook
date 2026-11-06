"""Export synthetic parcel screening geometries to an auditable GeoPackage.

No parcel ownership data or external source retrieval. Layers contain geometry
as provided; exported parcel polygons are not surveyed property boundaries.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd

import importlib.util

_DETAIL = Path(__file__).resolve().parent / "parcel_detail.py"
_SPEC = importlib.util.spec_from_file_location("parcel_screening_detail", _DETAIL)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
parcel_screen = _MODULE.parcel_screen


def export_geopackage(parcels: gpd.GeoDataFrame, constraints: gpd.GeoDataFrame,
                      coverage: gpd.GeoDataFrame, destination: str | Path) -> Path:
    """Export parcels, known overlap polygons, and source-coverage footprints.

    The caller must verify source metadata and write the tabular constraint
    matrix separately. No buffer or geometry simplification is applied.
    """
    rows = parcel_screen(parcels, constraints, coverage)
    if not rows:
        raise ValueError("No parcel/type screening results")
    path = Path(destination)
    if path.suffix.lower() != ".gpkg":
        raise ValueError("Destination must have .gpkg extension")
    if path.exists():
        raise FileExistsError("Refusing to overwrite an existing GeoPackage")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Copy only stable parcel identifiers and geometry to avoid exporting
    # owner names, assessment attributes, or other incidental private fields.
    parcel_layer = gpd.GeoDataFrame(
        {"parcel_id": parcels.parcel_id.astype(str)},
        geometry=parcels.geometry.copy(), crs=parcels.crs)
    parcel_layer.to_file(path, layer="parcels", driver="GPKG", index=False)

    cover_records = []
    overlap_records = []
    types = sorted(set(constraints.constraint_type) | set(coverage.constraint_type))
    for parcel_id, geometry in zip(parcels.parcel_id, parcels.geometry):
        for kind in types:
            extents = coverage.geometry.loc[coverage.constraint_type == kind]
            extent = extents.union_all() if len(extents) else None
            if extent is None:
                continue
            known = geometry.intersection(extent)
            if known.is_empty or known.area <= 0:
                continue
            cover_records.append({"parcel_id": str(parcel_id),
                                  "constraint_type": str(kind), "geometry": known})
            features = constraints.geometry.loc[constraints.constraint_type == kind]
            if len(features):
                overlap = known.intersection(features.union_all())
                if not overlap.is_empty and overlap.area > 0:
                    overlap_records.append({"parcel_id": str(parcel_id),
                                            "constraint_type": str(kind), "geometry": overlap})
    # Empty GeoPackage vector layers are not universally supported by drivers.
    # An absent layer therefore means no positive-area geometries were emitted;
    # inspect the separate tabular screening matrix for negative/unknown cases.
    for name, records in (("source_coverage", cover_records), ("known_overlaps", overlap_records)):
        if records:
            gpd.GeoDataFrame(records, geometry="geometry", crs=parcels.crs).to_file(
                path, layer=name, driver="GPKG", index=False)
    return path
