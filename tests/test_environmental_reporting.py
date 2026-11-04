"""Tests for deterministic parcel-level screening deliverables."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_csv_json_outputs_are_sorted_and_repeatable(tmp_path):
    screening = load("parcel_detail")
    reporting = load("reporting")
    import geopandas as gpd
    from shapely.geometry import box

    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame({"parcel_id": ["B", "A"]},
                               geometry=[box(500100, 3200000, 500200, 3200100),
                                         box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame({"constraint_type": ["wetlands"]},
                                   geometry=[box(500000, 3200000, 500050, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame({"constraint_type": ["wetlands"]},
                                geometry=[box(499900, 3199900, 500300, 3200200)], crs=crs)
    rows = screening.parcel_screen(parcels, constraints, coverage)
    csv_path, json_path = reporting.write_reports(rows, tmp_path)
    first_csv, first_json = csv_path.read_bytes(), json_path.read_bytes()
    reporting.write_reports(list(reversed(rows)), tmp_path)
    assert (csv_path.read_bytes(), json_path.read_bytes()) == (first_csv, first_json)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        result = list(csv.DictReader(handle))
    assert [row["parcel_id"] for row in result] == ["A", "B"]
    assert json.loads(first_json)["rows"][0]["known_overlap_m2"] == pytest.approx(5000)


def test_invalid_coverage_fails_closed(tmp_path):
    reporting = load("reporting")
    row = dict(parcel_id="A", constraint_type="wetlands", status="intersects",
               parcel_m2=100, parcel_acres=100 / 4046.8564224,
               covered_m2=50, unknown_m2=0, known_overlap_m2=60,
               known_overlap_acres=60 / 4046.8564224,
               known_overlap_pct_parcel=60, coverage_pct_parcel=50)
    with pytest.raises(ValueError, match="Contradictory|reconcile"):
        reporting.write_reports([row], tmp_path)
    assert not (tmp_path / "parcel_constraints.csv").exists()


def test_status_and_coverage_consistency(tmp_path):
    reporting = load("reporting")
    base = dict(parcel_id="A", constraint_type="wetlands", status="no_mapped_intersection",
                parcel_m2=100, parcel_acres=100 / 4046.8564224,
                covered_m2=100, unknown_m2=0, known_overlap_m2=0,
                known_overlap_acres=0, known_overlap_pct_parcel=0, coverage_pct_parcel=100)
    for change in (
        {"status": "intersects"},
        {"status": "partial_source_coverage"},
        {"status": "no_source_coverage"},
        {"status": "no_mapped_intersection", "known_overlap_m2": 5,
         "known_overlap_acres": 5 / 4046.8564224, "known_overlap_pct_parcel": 5},
    ):
        with pytest.raises(ValueError, match="contradicts|requires"):
            reporting.write_reports([{**base, **change}], tmp_path)


def test_source_register_validated_and_complete(tmp_path):
    reporting = load("reporting")
    row = dict(parcel_id="A", constraint_type="wetlands", status="no_mapped_intersection",
               parcel_m2=100, parcel_acres=100 / 4046.8564224,
               covered_m2=100, unknown_m2=0, known_overlap_m2=0,
               known_overlap_acres=0, known_overlap_pct_parcel=0, coverage_pct_parcel=100)
    source = dict(constraint_type="wetlands", dataset_id="synthetic-nwi",
                  source_url="https://example.org/source",
                  accessed_utc="2026-11-02T12:00:00Z", effective_date=None,
                  horizontal_accuracy_m=None, native_resolution_m=None,
                  boundary_basis="synthetic")
    _, json_path = reporting.write_reports([row], tmp_path, sources=[source])
    assert json.loads(json_path.read_text())["provenance_status"] == "validated"
    for changed in (
        {**source, "source_url": "http://example.org/source"},
        {**source, "accessed_utc": "2026-11-02"},
        {**source, "constraint_type": "flood"},
        {**source, "native_resolution_m": -5},
    ):
        with pytest.raises(ValueError):
            reporting.write_reports([row], tmp_path, sources=[changed])


@pytest.mark.parametrize("covered_width,feature_width,expected", [
    (100, 5e-8, "intersects"),
    (5e-8, 100, "partial_source_coverage"),
])
def test_tiny_positive_areas_survive_screening_and_reporting(
        tmp_path, covered_width, feature_width, expected):
    import geopandas as gpd
    from shapely.geometry import box

    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame({"parcel_id": ["A"]},
                               geometry=[box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame({"constraint_type": ["wetlands"]},
                                   geometry=[box(500000, 3200000, 500000 + feature_width, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame({"constraint_type": ["wetlands"]},
                                geometry=[box(500000, 3200000, 500000 + covered_width, 3200100)], crs=crs)
    rows = load("parcel_detail").parcel_screen(parcels, constraints, coverage)
    assert rows[0]["status"] == expected
    assert 0 < rows[0]["known_overlap_m2"] < 1e-5

    reporting = load("reporting")
    _, json_path = reporting.write_reports(rows, tmp_path)
    assert json.loads(json_path.read_text())["rows"][0]["status"] == expected

    # Numeric reconciliation tolerance must not turn a positive measurement
    # into a negative finding or an assertion of absent source coverage.
    false_negative = "no_mapped_intersection" if expected == "intersects" else "no_source_coverage"
    with pytest.raises(ValueError, match="contradicts"):
        reporting.validate_rows([{**rows[0], "status": false_negative}])
