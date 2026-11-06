"""Generate a reproducible synthetic parcel-screening deliverable bundle.

The manifest hashes every deliverable and records the analysis CRS. This
example deliberately does not fetch parcel or environmental datasets.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re

import geopandas as gpd

DELIVERABLE_NAMES = {
    "parcel_constraints.csv", "parcel_screening.json",
    "parcel_screening.gpkg", "parcel_review_map.png",
}


def _load(name: str):
    location = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"parcel_bundle_{name}", location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_bundle(parcels: gpd.GeoDataFrame, constraints: gpd.GeoDataFrame,
                 coverage: gpd.GeoDataFrame, destination: str | Path,
                 sources: list[dict]) -> Path:
    """Build into a new directory only; reject incomplete source registers."""
    directory = Path(destination)
    if directory.exists():
        raise FileExistsError("Bundle directory already exists")
    if not isinstance(sources, list):
        raise ValueError("A source-register list is required")
    screening = _load("parcel_detail")
    reporting = _load("reporting")
    exporter = _load("geopackage_export")
    mapping = _load("review_map")
    rows = screening.parcel_screen(parcels, constraints, coverage)
    reporting.validate_rows(rows)
    reporting.validate_sources(sources, {row["constraint_type"] for row in rows})
    directory.mkdir(parents=True)
    try:
        csv_path, json_path = reporting.write_reports(rows, directory, sources=sources)
        gpkg_path = exporter.export_geopackage(
            parcels, constraints, coverage, directory / "parcel_screening.gpkg"
        )
        map_path = mapping.render_review_map(parcels, constraints, coverage, directory / "parcel_review_map.png")
        files = (csv_path, json_path, gpkg_path, map_path)
        manifest = {
            "method": "synthetic_parcel_screening_bundle_v1",
            "analysis_crs": parcels.crs.to_string(),
            "parcel_count": len(parcels),
            "constraint_result_count": len(rows),
            "constraint_types": sorted({row["constraint_type"] for row in rows}),
            "source_count": len(sources),
            "disclaimer": "Preliminary GIS screening; not a survey or regulatory determination.",
            "files": [
                {"filename": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
                for path in sorted(files, key=lambda path: path.name)
            ],
        }
        (directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return directory
    except Exception:
        # Never leave a partially populated deliverable directory behind.
        for path in directory.iterdir():
            if path.is_file():
                path.unlink()
        directory.rmdir()
        raise


def verify_bundle(directory: str | Path) -> bool:
    """Check the complete flat bundle against its manifest, including checksums.

    All four deliverables must be regular files, with no symlinks or unlisted
    directories. This verifies consistency, not source accuracy or authenticity.
    """
    directory = Path(directory)
    members = list(directory.iterdir())
    if (any(path.is_symlink() or not path.is_file() for path in members)
            or {path.name for path in members} != DELIVERABLE_NAMES | {"manifest.json"}):
        raise ValueError("Bundle file inventory mismatch")
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("method") != "synthetic_parcel_screening_bundle_v1":
        raise ValueError("Unsupported bundle manifest")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("Bundle manifest files must be a list")
    names = []
    for entry in entries:
        if (not isinstance(entry, dict) or not isinstance(entry.get("filename"), str)
                or type(entry.get("bytes")) is not int or entry["bytes"] < 0
                or not isinstance(entry.get("sha256"), str)
                or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None):
            raise ValueError("Invalid bundle manifest file entry")
        names.append(entry["filename"])
    if len(names) != len(set(names)) or set(names) != DELIVERABLE_NAMES:
        raise ValueError("Bundle manifest file inventory mismatch")
    for entry in entries:
        path = directory / entry["filename"]
        if path.stat().st_size != entry["bytes"] or _sha256(path) != entry["sha256"]:
            raise ValueError(f"Bundle checksum mismatch: {path.name}")
    return True
