"""Rank 1 synthetic environmental exhibit handoff regression coverage.

Desktop-only test fixture. Not a field wetland delineation, jurisdictional
determination, Phase I ESA, survey, professional certification or permit approval.
Checks source/date and uncertainty provenance, not real-world environmental truth.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

BASE = Path(__file__).resolve().parents[1] / "examples/12-environmental-screening"
DEMO = BASE / "demo_bundle.py"
EXHIBIT = BASE / "exhibit_prep.py"


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          text=True, capture_output=True, check=False)


def test_handoff_has_verified_source_register_disclaimer_and_checksums(tmp_path):
    bundle = tmp_path / "bundle"
    destination = tmp_path / "exhibit"
    assert run(DEMO, bundle).returncode == 0
    result = run(EXHIBIT, bundle, destination)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((destination / "exhibit_manifest.json").read_text(encoding="utf-8"))
    sources = json.loads((destination / "source_register.json").read_text(encoding="utf-8"))
    screening = json.loads((destination / "parcel_screening.json").read_text(encoding="utf-8"))
    notice = (destination / "LIMITATIONS.txt").read_text(encoding="utf-8")
    assert manifest["data"] == "synthetic"
    assert manifest["method"] == "rank1_synthetic_exhibit_handoff_v1"
    assert manifest["analysis_crs"] == "EPSG:32617"
    assert len(sources) == manifest["source_count"] == 2
    assert {x["constraint_type"] for x in sources} == {
        "wetland_inventory", "flood_hazard"}
    assert all(x["source_url"].startswith("https://example.org/synthetic/")
               and x["accessed_utc"].endswith("Z") and x["boundary_basis"] for x in sources)
    assert any(row["status"] == "no_source_coverage" for row in screening["rows"])
    assert any(row["status"] == "partial_source_coverage" for row in screening["rows"])
    for keyword in ["SYNTHETIC", "delineation", "jurisdictional", "Phase I", "survey", "certification"]:
        assert keyword in notice
    expected_files = {
        "parcel_constraints.csv", "parcel_screening.json", "parcel_screening.gpkg",
        "parcel_review_map.png", "manifest.json", "source_register.json", "LIMITATIONS.txt"}
    assert {x["filename"] for x in manifest["file_inventory"]} == expected_files
    for item in manifest["file_inventory"]:
        p = destination / item["filename"]
        assert item["bytes"] == p.stat().st_size
        assert item["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()
    assert {p.name for p in destination.iterdir()} == expected_files | {"exhibit_manifest.json"}


def test_missing_provenance_is_rejected_with_no_partial_handoff(tmp_path):
    bundle = tmp_path / "bundle"
    dest = tmp_path / "exhibit"
    assert run(DEMO, bundle).returncode == 0
    # Tamper with a report without updating the signed-by-checksum bundle manifest.
    report = bundle / "parcel_screening.json"
    payload = json.loads(report.read_text())
    payload["source_register"] = []
    report.write_text(json.dumps(payload), encoding="utf-8")
    result = run(EXHIBIT, bundle, dest)
    assert result.returncode != 0
    assert "checksum" in result.stderr.lower()
    assert not dest.exists()


def test_existing_handoff_is_not_overwritten(tmp_path):
    bundle = tmp_path / "bundle"
    dest = tmp_path / "exhibit"
    assert run(DEMO, bundle).returncode == 0
    assert run(EXHIBIT, bundle, dest).returncode == 0
    original = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in dest.iterdir()}
    result = run(EXHIBIT, bundle, dest)
    assert result.returncode == 2
    assert "already exists" in result.stderr
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in dest.iterdir()} == original
