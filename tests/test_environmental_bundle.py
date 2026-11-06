"""Synthetic parcel bundle integrity tests."""
import importlib.util
import json
from pathlib import Path
import shutil

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


def test_unlisted_nested_files_fail_inventory_check(tmp_path):
    parcels, constraints, coverage, sources = inputs()
    path = bundle.build_bundle(parcels, constraints, coverage, tmp_path / "deliverable", sources)
    nested = path / "unlisted"
    nested.mkdir()
    (nested / "extra.txt").write_text("not declared in manifest", encoding="utf-8")
    with pytest.raises(ValueError, match="inventory"):
        bundle.verify_bundle(path)


@pytest.mark.parametrize("filename", ["manifest.json", "parcel_constraints.csv"])
def test_symlinked_bundle_members_are_rejected(tmp_path, filename):
    parcels, constraints, coverage, sources = inputs()
    path = bundle.build_bundle(parcels, constraints, coverage, tmp_path / "deliverable", sources)
    member = path / filename
    external = tmp_path / ("external-" + filename)
    shutil.copyfile(member, external)
    member.unlink()
    try:
        member.symlink_to(external)
    except OSError:
        pytest.skip("Symbolic-link creation is unavailable on this platform")
    with pytest.raises(ValueError, match="inventory"):
        bundle.verify_bundle(path)


def test_empty_bundle_cannot_verify_as_a_complete_deliverable(tmp_path):
    path = tmp_path / "empty"
    path.mkdir()
    (path / "manifest.json").write_text(json.dumps({"files": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="inventory|manifest"):
        bundle.verify_bundle(path)


def test_duplicate_manifest_members_are_rejected(tmp_path):
    parcels, constraints, coverage, sources = inputs()
    path = bundle.build_bundle(parcels, constraints, coverage, tmp_path / "deliverable", sources)
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"].append(dict(manifest["files"][0]))
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="inventory|manifest"):
        bundle.verify_bundle(path)


@pytest.mark.parametrize("renamed", ["parcels", "constraints", "coverage", "all"])
def test_bundle_uses_each_layers_active_geometry(tmp_path, renamed):
    parcels, constraints, coverage, sources = inputs()
    frames = {"parcels": parcels, "constraints": constraints, "coverage": coverage}
    for name in frames:
        if renamed in (name, "all"):
            frames[name] = frames[name].rename_geometry("active footprint")
            # An inactive column named geometry must not substitute for the
            # real geometry, or leak incidental input attributes into export.
            frames[name]["geometry"] = "incidental metadata"
    path = bundle.build_bundle(frames["parcels"], frames["constraints"], frames["coverage"],
                               tmp_path / "deliverable", sources)
    assert bundle.verify_bundle(path)
    row = json.loads((path / "parcel_screening.json").read_text(encoding="utf-8"))["rows"][0]
    assert row["parcel_m2"] == pytest.approx(10000)
    assert row["known_overlap_m2"] == pytest.approx(5000)
    exported = gpd.read_file(path / "parcel_screening.gpkg", layer="parcels")
    assert set(exported.columns) == {"parcel_id", "geometry"}
    assert exported.geometry.area.iloc[0] == pytest.approx(10000)
    for name, frame in frames.items():
        if renamed in (name, "all"):
            assert frame.geometry.name == "active footprint"
            assert frame["geometry"].iloc[0] == "incidental metadata"


def test_reviewer_map_keeps_parcels_visible_with_regional_sources(tmp_path, monkeypatch):
    parcels, constraints, coverage, sources = inputs()
    coverage.geometry = [box(450000, 3150000, 550000, 3250000)]
    constraints = gpd.GeoDataFrame(
        {"constraint_type": ["wetlands", "wetlands"]},
        geometry=[constraints.geometry.iloc[0], box(540000, 3240000, 540100, 3240100)],
        crs=parcels.crs)
    mapping = bundle._load("review_map")
    saved = {}
    original_save = mapping.plt.Figure.savefig

    def capture_view(figure, *args, **kwargs):
        saved["xlim"] = figure.axes[0].get_xlim()
        saved["ylim"] = figure.axes[0].get_ylim()
        return original_save(figure, *args, **kwargs)

    monkeypatch.setattr(mapping.plt.Figure, "savefig", capture_view)
    path = bundle.build_bundle(parcels, constraints, coverage, tmp_path / "deliverable", sources)
    assert bundle.verify_bundle(path)
    left, right = saved["xlim"]
    bottom, top = saved["ylim"]
    assert left < 500000 < 500100 < right
    assert bottom < 3200000 < 3200100 < top
    assert right - left < 500, "A 100 m parcel must remain visible inside a 100 km coverage layer"
    assert top - bottom < 500
