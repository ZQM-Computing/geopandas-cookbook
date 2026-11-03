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
