"""Source metadata and parcel-boundary review regression tests."""
import importlib.util
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

PATH = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening/source_quality.py"
spec = importlib.util.spec_from_file_location("source_quality", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_source_accuracy_must_be_explicit_or_unknown():
    record = {
        "dataset_id": "synthetic-parcels", "source_url": "https://example.org/data",
        "accessed_utc": "2026-11-03T00:00:00Z", "effective_date": None,
        "horizontal_accuracy_m": None, "native_resolution_m": 1.0,
        "boundary_basis": "synthetic",
    }
    assert module.validate_source_record(record)["horizontal_accuracy_m"] is None
    with pytest.raises(ValueError, match="horizontal_accuracy_m"):
        module.validate_source_record({**record, "horizontal_accuracy_m": -1})
    with pytest.raises(ValueError, match="Missing source metadata"):
        module.validate_source_record({k: v for k, v in record.items() if k != "boundary_basis"})


def test_boundary_proximity_is_a_review_flag_not_an_overlap():
    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame({"parcel_id": ["P1"]},
                               geometry=[box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame({"constraint_type": ["wetland_inventory"]},
                                   geometry=[box(500105, 3200020, 500120, 3200080)], crs=crs)
    assert module.boundary_review_flags(parcels, constraints, 4) == []
    flags = module.boundary_review_flags(parcels, constraints, 5)
    assert len(flags) == 1
    assert flags[0]["boundary_distance_m"] == pytest.approx(5)
    assert flags[0]["flag"] == "boundary_proximity_review"


@pytest.mark.parametrize("tolerance", [0, -1, float("nan")])
def test_invalid_review_tolerance_is_rejected(tolerance):
    parcels = gpd.GeoDataFrame({"parcel_id": ["P1"]},
                               geometry=[box(0, 0, 10, 10)], crs="EPSG:32617")
    constraints = gpd.GeoDataFrame({"constraint_type": ["wetland_inventory"]},
                                   geometry=[box(15, 0, 20, 10)], crs="EPSG:32617")
    with pytest.raises(ValueError, match="tolerance_m"):
        module.boundary_review_flags(parcels, constraints, tolerance)
