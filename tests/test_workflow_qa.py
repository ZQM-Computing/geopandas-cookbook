"""Acceptance tests for the buyer-facing synthetic workflow demonstration."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workflow_qa", ROOT / "demos/workflow_qa.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
FIXTURE = ROOT / "demos/workflow-input.json"


def test_every_row_accounted_for_with_boundary_and_duplicate_policy():
    report = demo.build_report(FIXTURE.read_bytes())
    assert report["summary"] == {"input": 8, "accepted": 2, "rejected": 6}
    assert [r["properties"]["record_id"] for r in report["accepted"]] == ["inside", "edge"]
    assert [r["reasons"] for r in report["rejected"]] == [
        ["outside_boundary"], ["duplicate_id"], ["duplicate_id"], ["missing_name"],
        ["missing_or_unreadable_geometry"], ["not_point"],
    ]


@pytest.mark.parametrize("field,value", [
    ("source_crs", None), ("source_crs", "EPSG:0"),
    ("analysis_crs", "EPSG:4326"), ("analysis_crs", "not-a-crs"),
    ("boundary_wkt", "POLYGON ((0 0, 1 1, 1 0, 0 1, 0 0))"),
    ("boundary_wkt", ["POLYGON ((0 0, 1 0, 1 1, 0 0))"]),
    ("boundary_wkt", "this is not WKT"),
    ("records", []), ("records", [None]),
])
def test_bad_batch_preserves_last_success(tmp_path, field, value):
    output = tmp_path / "report.json"
    demo.run(FIXTURE, output)
    previous = output.read_bytes()
    batch = json.loads(FIXTURE.read_bytes())
    batch[field] = value
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(batch))
    with pytest.raises(ValueError):
        demo.run(broken, output)
    assert output.read_bytes() == previous


def test_repeatability_and_input_identity(tmp_path):
    output = tmp_path / "report.json"
    demo.run(FIXTURE, output)
    previous = output.read_bytes()
    demo.run(FIXTURE, output)
    assert output.read_bytes() == previous
    altered = FIXTURE.read_bytes() + b"\n"
    assert demo.build_report(altered)["input_sha256"] != json.loads(previous)["input_sha256"]


def test_projection_and_invalid_coordinates():
    batch = json.loads(FIXTURE.read_bytes())
    batch.update(source_crs="EPSG:4326", boundary_wkt="POLYGON ((-81.1 28.9, -80.9 28.9, -80.9 29.1, -81.1 29.1, -81.1 28.9))")
    batch["records"] = [
        {"record_id": "ok", "name": "Projected", "wkt": "POINT (-81 29)"},
        {"record_id": "bad", "name": "Latitude", "wkt": "POINT (-81 100)"},
    ]
    report = demo.build_report(json.dumps(batch).encode())
    assert report["summary"] == {"input": 2, "accepted": 1, "rejected": 1}
    assert report["accepted"][0]["geometry"]["coordinates"][0] == pytest.approx(500000)
    assert report["rejected"][0]["reasons"] == ["untransformable_geometry"]


def test_failed_publication_leaves_previous_bundle(tmp_path, monkeypatch):
    output = tmp_path / "report.json"
    demo.run(FIXTURE, output)
    previous = output.read_bytes()
    def fail(*args):
        raise OSError("simulated publication failure")
    monkeypatch.setattr(demo.os, "replace", fail)
    with pytest.raises(OSError):
        demo.run(FIXTURE, output)
    assert output.read_bytes() == previous
    assert not list(tmp_path.glob(".qa-*"))


def test_cannot_overwrite_input(tmp_path):
    source = tmp_path / "input.json"
    source.write_bytes(FIXTURE.read_bytes())
    with pytest.raises(ValueError, match="overwrite input"):
        demo.run(source, source)
    assert source.read_bytes() == FIXTURE.read_bytes()


@pytest.mark.parametrize("wkt", [
    ["POINT (500500 3200500)"],
    {"geometry": "POINT (500500 3200500)"},
    123,
    False,
    None,
    "NOT A VALID WKT",
])
def test_malformed_record_wkt_is_rejected_without_aborting_valid_records(wkt):
    batch = json.loads(FIXTURE.read_bytes())
    batch["records"].append({"record_id": "malformed-extra", "name": "Bad geometry", "wkt": wkt})
    report = demo.build_report(json.dumps(batch).encode())
    assert report["summary"] == {"input": 9, "accepted": 2, "rejected": 7}
    assert [r["properties"]["record_id"] for r in report["accepted"]] == ["inside", "edge"]
    assert report["rejected"][-1]["reasons"] == ["missing_or_unreadable_geometry"]
