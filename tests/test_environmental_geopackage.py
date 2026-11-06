"""GeoPackage export regression tests for synthetic parcel geometries."""
import importlib.util
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening"
sys.path.insert(0, str(EXAMPLE))
spec = importlib.util.spec_from_file_location("geopackage_export", EXAMPLE / "geopackage_export.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_geopackage_contains_parcels_coverage_and_union_overlap(tmp_path):
    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame({"parcel_id": ["P1"], "owner": ["NOT FOR EXPORT"]},
                               geometry=[box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame({"constraint_type": ["wetland", "wetland"]},
                                   geometry=[box(500000, 3200000, 500050, 3200100),
                                             box(500000, 3200000, 500050, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame({"constraint_type": ["wetland"]},
                                geometry=[box(499900, 3199900, 500200, 3200200)], crs=crs)
    destination = module.export_geopackage(parcels, constraints, coverage, tmp_path / "screening.gpkg")
    parcel_output = gpd.read_file(destination, layer="parcels")
    known = gpd.read_file(destination, layer="known_overlaps")
    source_coverage = gpd.read_file(destination, layer="source_coverage")
    assert "owner" not in parcel_output.columns
    assert parcel_output.crs == parcels.crs
    assert known.geometry.area.sum() == pytest.approx(5000)
    assert source_coverage.geometry.area.sum() == pytest.approx(10000)
    with pytest.raises(FileExistsError):
        module.export_geopackage(parcels, constraints, coverage, destination)


def test_no_overlap_still_exports_parcel_and_coverage(tmp_path):
    crs = "EPSG:32617"
    parcels = gpd.GeoDataFrame({"parcel_id": ["P1"]},
                               geometry=[box(500000, 3200000, 500100, 3200100)], crs=crs)
    constraints = gpd.GeoDataFrame({"constraint_type": ["flood"]},
                                   geometry=[box(500200, 3200000, 500300, 3200100)], crs=crs)
    coverage = gpd.GeoDataFrame({"constraint_type": ["flood"]},
                                geometry=[box(499900, 3199900, 500200, 3200200)], crs=crs)
    path = module.export_geopackage(parcels, constraints, coverage, tmp_path / "screening.gpkg")
    assert len(gpd.read_file(path, layer="parcels")) == 1
    assert len(gpd.read_file(path, layer="source_coverage")) == 1
    assert "known_overlaps" not in set(gpd.list_layers(path)["name"])
