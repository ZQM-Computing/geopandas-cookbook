"""Synthetic parcel bundle integrity tests."""
import importlib.util
import json
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

SOURCE = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening/bundle.py"
spec = importlib.util.spec_from_file_location("parcel_bundle", SOURCE)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def inputs():
    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame({"parcel_id": ["P1"]},
                               geometry=[box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame({"constraint_type": ["wetlands"]},
                                   geometry=[box(500000, 3200000, 500050, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame({"constraint_type": ["wetlands"]},
                                geometry=[box(499900, 3199900, 500200, 3200200)], crs=crs)
    sources = [{
        "constraint_type": "wetlands", "dataset_id": "synthetic-nwi",
        "source_url": "https://example.org/wetlands",
        "accessed_utc": "2026-11-02T12:00:00Z", "effective_date": None,
        "horizontal_accuracy_m": None, "native_resolution_m": None,
        "boundary_basis": "synthetic",
    }]
    return parcels, constraints, coverage, sources


def test_bundle_integrity_and_manifest(tmp_path):
    parcels, constraints, coverage, sources = inputs()
    path = bundle.build_bundle(parcels, constraints, coverage, tmp_path / "deliverable", sources)
    assert bundle.verify_bundle(path)
    manifest = json.loads((path / "manifest.json").read_text())
    assert manifest["parcel_count"] == 1
    assert manifest["source_count"] == 1
    assert len(manifest["files"]) == 4
    assert (path / "parcel_review_map.png").read_bytes().startswith(bytes((137, 80, 78, 71)))
    assert all(len(entry["sha256"]) == 64 for entry in manifest["files"])
    with pytest.raises(FileExistsError):
        bundle.build_bundle(parcels, constraints, coverage, path, sources)


def test_modified_report_fails_integrity_check(tmp_path):
    parcels, constraints, coverage, sources = inputs()
    path = bundle.build_bundle(parcels, constraints, coverage, tmp_path / "deliverable", sources)
    with (path / "parcel_constraints.csv").open("a", encoding="utf-8") as stream:
        stream.write("tampered\n")
    with pytest.raises(ValueError, match="checksum"):
        bundle.verify_bundle(path)


def test_missing_source_register_rejected_before_creating_output(tmp_path):
    parcels, constraints, coverage, _ = inputs()
    target = tmp_path / "deliverable"
    with pytest.raises(ValueError, match="Source register"):
        bundle.build_bundle(parcels, constraints, coverage, target, [])
    assert not target.exists()
