"""The documented synthetic bundle command must produce reviewable, preserved outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/12-environmental-screening/demo_bundle.py"


def test_synthetic_bundle_cli_and_existing_output_preservation(tmp_path):
    destination = tmp_path / "parcel review"
    command = [sys.executable, str(DEMO), str(destination)]
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    receipt = json.loads(result.stdout)
    assert receipt["data"] == "synthetic"
    assert receipt["parcel_count"] == 2
    assert receipt["constraint_result_count"] == 4
    assert receipt["integrity_verified"] is True
    assert set(receipt["files"]) == {
        "manifest.json", "parcel_constraints.csv", "parcel_screening.json",
        "parcel_screening.gpkg", "parcel_review_map.png",
    }
    report = json.loads((destination / "parcel_screening.json").read_text())
    rows = {(row["parcel_id"], row["constraint_type"]): row for row in report["rows"]}
    assert len(rows) == 4
    assert rows["DEMO-P1", "wetland_inventory"]["known_overlap_m2"] == 5000
    assert rows["DEMO-P2", "flood_hazard"]["covered_m2"] == 5000
    assert rows["DEMO-P2", "flood_hazard"]["known_overlap_m2"] == 2500
    assert rows["DEMO-P2", "wetland_inventory"]["status"] == "no_source_coverage"
    assert (destination / "parcel_review_map.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir()}
    repeated = subprocess.run(command, text=True, capture_output=True)
    assert repeated.returncode == 2
    assert "already exists" in repeated.stderr
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir()} == before
