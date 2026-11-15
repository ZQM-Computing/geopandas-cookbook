"""Build a synthetic, reviewer-oriented environmental exhibit handoff directory.

Rank 1 environmental GIS production workflow demonstration; SYNTHETIC inputs.
Desktop work only, NOT a field wetland delineation, jurisdictional
determination, Phase I ESA, boundary survey, professional certification,
engineering opinion or permit approval. Source/date records and uncertainty
must accompany exports; qualified professionals verify real-world decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from bundle import DELIVERABLE_NAMES, verify_bundle
from reporting import validate_rows, validate_sources

NOTICE = """SYNTHETIC ENVIRONMENTAL GIS EXHIBIT HANDOFF - DEMONSTRATION ONLY

Desktop GIS / database preparation only. NOT a field wetland delineation,
jurisdictional determination, Phase I environmental site assessment (ESA),
boundary survey, professional certification, engineering opinion, or permit
approval. All features and source records in the documented demo are synthetic.
Review current authoritative sources and verify every mapped indicator with
qualified field professionals before property purchase, development or permits.

Read source_register.json (publisher, source URL, retrieval date, limitations)
and parcel_screening.json (coverage, unknown area, and screening status).
A no-mapped-intersection finding is not proof that a constraint is absent.
GeoPackage geometries are illustrative; not certified parcel boundaries.
Client approval, sheet layout, professional signoff, licensing, and project
specific map figures are out of scope. This is NOT a completed client project.
"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_exhibit_package(bundle_dir: str | Path, destination: str | Path) -> Path:
    """Copy a verified screening bundle plus explicit source and limitations files.

    Refuse existing destinations and missing provenance; never mutate source.
    Integrity checks verify bundle bytes, not source authority or field truth.
    """
    bundle_dir = Path(bundle_dir)
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError("Exhibit destination already exists")
    verify_bundle(bundle_dir)
    report = json.loads((bundle_dir / "parcel_screening.json").read_text(encoding="utf-8"))
    rows = validate_rows(report.get("rows", []))
    if not rows or report.get("provenance_status") != "validated":
        raise ValueError("Validated source register and screening rows are required")
    sources = validate_sources(
        report.get("source_register", []),
        {row["constraint_type"] for row in rows},
    )
    destination.mkdir(parents=True)
    try:
        for name in sorted(DELIVERABLE_NAMES | {"manifest.json"}):
            shutil.copyfile(bundle_dir / name, destination / name)
        (destination / "source_register.json").write_text(
            json.dumps(sources, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
        (destination / "LIMITATIONS.txt").write_text(NOTICE, encoding="utf-8")
        files = sorted(path for path in destination.iterdir() if path.is_file())
        handoff = {
            "method": "rank1_synthetic_exhibit_handoff_v1",
            "data": "synthetic",
            "disclaimer": "Desktop-only demonstration; no professional or regulatory determination.",
            "analysis_crs": json.loads(
                (bundle_dir / "manifest.json").read_text(encoding="utf-8")
            )["analysis_crs"],
            "source_count": len(sources),
            "file_inventory": [
                {"filename": p.name, "sha256": _sha256(p), "bytes": p.stat().st_size}
                for p in files
            ],
        }
        (destination / "exhibit_manifest.json").write_text(
            json.dumps(handoff, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
        return destination
    except Exception:
        # Leave no partial handoff if a write fails.
        shutil.rmtree(destination)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Existing verified synthetic demo bundle")
    parser.add_argument("destination", type=Path, help="New exhibit output directory")
    args = parser.parse_args()
    try:
        package = build_exhibit_package(args.bundle, args.destination)
    except (ValueError, FileExistsError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps({"data": "synthetic", "package": str(package.resolve()),
                      "file_count": len(list(package.iterdir()))}, sort_keys=True))


if __name__ == "__main__":
    main()
