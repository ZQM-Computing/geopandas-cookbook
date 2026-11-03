"""Parcel-level synthetic screening regression cases."""
import importlib.util
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

PATH = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening/parcel_detail.py"
spec = importlib.util.spec_from_file_location("parcel_detail", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def layer(data, geometries, crs="EPSG:32617"):
    return gpd.GeoDataFrame(data, geometry=geometries, crs=crs)


def test_two_parcels_have_independent_area_and_overlap():
    parcels = layer({"parcel_id": ["A", "B"]},
                    [box(500000, 3200000, 500100, 3200100),
                     box(500100, 3200000, 500200, 3200100)])
    constraints = layer({"constraint_type": ["nwi", "nwi"]},
                        [box(500000, 3200000, 500050, 3200100),
                         box(500000, 3200000, 500050, 3200100)])
    coverage = layer({"constraint_type": ["nwi"]},
                     [box(499900, 3199900, 500300, 3200200)])
    rows = {row["parcel_id"]: row for row in mod.parcel_screen(parcels, constraints, coverage)}
    assert rows["A"]["known_overlap_m2"] == pytest.approx(5000)
    assert rows["A"]["known_overlap_pct_parcel"] == pytest.approx(50)
    assert rows["A"]["parcel_acres"] == pytest.approx(10000 / 4046.8564224)
    assert rows["B"]["known_overlap_m2"] == pytest.approx(0)
    assert rows["B"]["status"] == "no_mapped_intersection"
    assert rows["A"]["unknown_m2"] == 0


def test_partial_coverage_preserves_known_overlap_and_unknown_area():
    parcels = layer({"parcel_id": ["A"]}, [box(500000, 3200000, 500100, 3200100)])
    constraints = layer({"constraint_type": ["nwi"]},
                        [box(500000, 3200000, 500100, 3200100)])
    coverage = layer({"constraint_type": ["nwi"]},
                     [box(500000, 3200000, 500050, 3200100)])
    row = mod.parcel_screen(parcels, constraints, coverage)[0]
    assert row["status"] == "partial_source_coverage"
    assert row["covered_m2"] == pytest.approx(5000)
    assert row["unknown_m2"] == pytest.approx(5000)
    assert row["known_overlap_m2"] == pytest.approx(5000)
    assert row["coverage_pct_parcel"] == pytest.approx(50)


def test_boundary_touch_is_not_area_overlap():
    parcels = layer({"parcel_id": ["A"]}, [box(500000, 3200000, 500100, 3200100)])
    constraints = layer({"constraint_type": ["nwi"]},
                        [box(500100, 3200000, 500200, 3200100)])
    coverage = layer({"constraint_type": ["nwi"]},
                     [box(499900, 3199900, 500300, 3200200)])
    row = mod.parcel_screen(parcels, constraints, coverage)[0]
    assert row["status"] == "no_mapped_intersection"
    assert row["known_overlap_m2"] == 0


def test_reject_duplicate_parcel_ids():
    parcels = layer({"parcel_id": ["A", "A"]},
                    [box(0, 0, 100, 100), box(100, 0, 200, 100)])
    constraints = layer({"constraint_type": ["nwi"]}, [box(0, 0, 50, 100)])
    coverage = layer({"constraint_type": ["nwi"]}, [box(-10, -10, 210, 110)])
    with pytest.raises(ValueError, match="unique"):
        mod.parcel_screen(parcels, constraints, coverage)


@pytest.mark.parametrize("crs", ["EPSG:4326", "EPSG:2277"])
def test_reject_non_metre_crs(crs):
    parcels = layer({"parcel_id": ["A"]}, [box(0, 0, 100, 100)], crs)
    constraints = layer({"constraint_type": ["nwi"]}, [box(0, 0, 50, 100)], crs)
    coverage = layer({"constraint_type": ["nwi"]}, [box(-10, -10, 110, 110)], crs)
    with pytest.raises(ValueError, match="projected metre|metre units"):
        mod.parcel_screen(parcels, constraints, coverage)
