"""Build the complete parcel review bundle using synthetic fixtures only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

from bundle import build_bundle, verify_bundle


def synthetic_inputs():
    """Two example parcels, duplicate overlaps and intentionally partial coverage."""
    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame(
        {"parcel_id": ["DEMO-P1", "DEMO-P2"]},
        geometry=[box(500000, 3200000, 500100, 3200100),
                  box(500100, 3200000, 500200, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame(
        {"constraint_type": ["wetland_inventory", "wetland_inventory", "flood_hazard"]},
        geometry=[box(500000, 3200000, 500050, 3200100),
                  box(500000, 3200000, 500050, 3200100),
                  box(500125, 3200000, 500175, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame(
        {"constraint_type": ["wetland_inventory", "flood_hazard"]},
        geometry=[box(500000, 3200000, 500100, 3200100),
                  box(500000, 3200000, 500150, 3200100)], crs=crs)
    sources = [{
        "constraint_type": kind,
        "dataset_id": "synthetic-" + kind,
        "source_url": "https://example.org/synthetic/" + kind,
        "accessed_utc": "2026-11-02T12:00:00Z",
        "effective_date": None,
        "horizontal_accuracy_m": None,
        "native_resolution_m": None,
        "boundary_basis": "synthetic fixture; not a surveyed boundary",
    } for kind in ["wetland_inventory", "flood_hazard"]]
    return parcels, constraints, coverage, sources


def main():
    parser = argparse.ArgumentParser(
        description="Build a synthetic parcel review bundle; no live data is downloaded.")
    parser.add_argument("destination", type=Path, help="New output directory; existing directories are refused")
    args = parser.parse_args()
    parcels, constraints, coverage, sources = synthetic_inputs()
    try:
        output = build_bundle(parcels, constraints, coverage, args.destination, sources)
        verify_bundle(output)
    except (ValueError, FileExistsError) as exc:
        parser.exit(2, f"error: {exc}\n")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    print(json.dumps({
        "data": "synthetic",
        "bundle": str(output.resolve()),
        "parcel_count": manifest["parcel_count"],
        "constraint_result_count": manifest["constraint_result_count"],
        "integrity_verified": True,
        "files": sorted(path.name for path in output.iterdir()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
