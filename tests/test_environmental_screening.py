"""Regression tests for the synthetic preliminary environmental screening example."""
import importlib.util
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

SOURCE = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening/run.py"
spec = importlib.util.spec_from_file_location("environmental_screening", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def frame(data, geometries, crs="EPSG:32617"):
    return gpd.GeoDataFrame(data, geometry=geometries, crs=crs)


def test_synthetic_screening_statuses_and_union():
    rows = {r["constraint_type"]: r for r in module.synthetic_demo()}
    assert rows["wetland_inventory"]["status"] == "intersects"
    assert rows["wetland_inventory"]["overlap_m2"] == pytest.approx(5000)
    assert rows["wetland_inventory"]["pct_site"] == pytest.approx(50)
    assert rows["flood_hazard"]["status"] == "no_mapped_intersection"
    assert rows["flood_hazard"]["overlap_m2"] == 0
    assert rows["soil_inventory"]["status"] == "no_source_coverage"
    assert rows["soil_inventory"]["overlap_m2"] is None


def test_partial_coverage_is_unknown_even_with_feature():
    sites = frame({"site_id": ["A"]}, [box(500000, 3200000, 500100, 3200100)])
    constraints = frame({"constraint_type": ["wetlands"]}, [box(500000, 3200000, 500050, 3200100)])
    coverage = frame({"constraint_type": ["wetlands"]}, [box(500000, 3200000, 500050, 3200100)])
    row = module.screen(sites, constraints, coverage)[0]
    assert row["status"] == "no_source_coverage"
    assert row["overlap_m2"] is None


@pytest.mark.parametrize("crs", ["EPSG:4326", "EPSG:2277"])
def test_reject_non_metre_crs(crs):
    sites = frame({"site_id": ["A"]}, [box(0, 0, 100, 100)], crs)
    constraints = frame({"constraint_type": ["wetlands"]}, [box(0, 0, 50, 100)], crs)
    coverage = frame({"constraint_type": ["wetlands"]}, [box(-10, -10, 110, 110)], crs)
    with pytest.raises(ValueError, match="projected CRS|metre units"):
        module.screen(sites, constraints, coverage)


def test_reject_duplicate_site_ids():
    sites = frame({"site_id": ["A", "A"]}, [box(0, 0, 100, 100), box(200, 0, 300, 100)])
    constraints = frame({"constraint_type": ["wetlands"]}, [box(0, 0, 50, 100)])
    coverage = frame({"constraint_type": ["wetlands"]}, [box(-10, -10, 310, 110)])
    with pytest.raises(ValueError, match="unique"):
        module.screen(sites, constraints, coverage)


def test_site_screening_accepts_renamed_active_geometry():
    sites = frame({"site_id": ["A"]}, [box(500000, 3200000, 500100, 3200100)])
    constraints = frame({"constraint_type": ["wetlands"]}, [box(500000, 3200000, 500050, 3200100)])
    coverage = frame({"constraint_type": ["wetlands"]}, [box(499900, 3199900, 500200, 3200200)])
    row = module.screen(*(f.rename_geometry("active footprint") for f in (sites, constraints, coverage)))[0]
    assert row["status"] == "intersects"
    assert row["overlap_m2"] == pytest.approx(5000)
