"""Deterministic parcel-level CSV and JSON report generation from synthetic screening.

No automatic fetches, no geocoding, and no regulatory conclusions.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

FIELDS = (
    "parcel_id", "constraint_type", "status", "parcel_m2", "parcel_acres",
    "covered_m2", "unknown_m2", "known_overlap_m2",
    "known_overlap_acres", "known_overlap_pct_parcel", "coverage_pct_parcel",
)


def validate_rows(rows: list[dict]) -> list[dict]:
    """Fail closed on malformed, duplicate, or contradictory screening rows."""
    validated = []
    seen = set()
    for row in rows:
        missing = set(FIELDS) - set(row)
        if missing:
            raise ValueError(f"Missing screening fields: {sorted(missing)}")
        key = (row["parcel_id"], row["constraint_type"])
        if not all(isinstance(v, str) and v.strip() for v in key) or key in seen:
            raise ValueError("Parcel/type keys must be unique nonempty strings")
        seen.add(key)
        if row["status"] not in ("intersects", "no_mapped_intersection",
                                 "partial_source_coverage", "no_source_coverage"):
            raise ValueError("Unknown screening status")
        for field in FIELDS[3:]:
            value = row[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{field} must be finite numeric")
            if value < 0:
                raise ValueError(f"{field} must not be negative")
        area = row["parcel_m2"]
        if area <= 0 or row["covered_m2"] > area + 1e-6 or row["known_overlap_m2"] > row["covered_m2"] + 1e-6:
            raise ValueError("Contradictory parcel or coverage areas")
        if abs(row["covered_m2"] + row["unknown_m2"] - area) > max(1e-6, area * 1e-9):
            raise ValueError("Coverage and unknown area do not reconcile")
        if abs(row["coverage_pct_parcel"] - 100 * row["covered_m2"] / area) > 1e-6:
            raise ValueError("Coverage percentage does not reconcile")
        if abs(row["known_overlap_pct_parcel"] - 100 * row["known_overlap_m2"] / area) > 1e-6:
            raise ValueError("Overlap percentage does not reconcile")
        status = row["status"]
        tol = max(1e-6, area * 1e-9)
        fully_covered = row["unknown_m2"] <= tol
        # Match the screening producer's positive-area semantics. Tolerance
        # reconciles arithmetic; it must not erase measured overlap/coverage.
        if status == "no_source_coverage" and row["covered_m2"] > 0:
            raise ValueError("no_source_coverage contradicts covered area")
        if status == "partial_source_coverage" and not (row["covered_m2"] > 0 and not fully_covered):
            raise ValueError("partial_source_coverage contradicts coverage")
        if status in ("intersects", "no_mapped_intersection") and not fully_covered:
            raise ValueError("Full-coverage status contradicts unknown area")
        if status == "intersects" and row["known_overlap_m2"] <= 0:
            raise ValueError("intersects requires positive overlap")
        if status == "no_mapped_intersection" and row["known_overlap_m2"] > 0:
            raise ValueError("no_mapped_intersection contradicts overlap")
        if abs(row["parcel_acres"] - area / 4046.8564224) > max(1e-8, area / 4046.8564224 * 1e-9):
            raise ValueError("Parcel acreage does not reconcile")
        if abs(row["known_overlap_acres"] - row["known_overlap_m2"] / 4046.8564224) > 1e-8:
            raise ValueError("Overlap acreage does not reconcile")
        validated.append({name: row[name] for name in FIELDS})
    return sorted(validated, key=lambda row: (row["parcel_id"], row["constraint_type"]))


def validate_sources(sources: list[dict], types: set[str]) -> list[dict]:
    """Require one traceable source record for each reported constraint type."""
    required = ("constraint_type", "dataset_id", "source_url", "accessed_utc",
                "effective_date", "horizontal_accuracy_m", "native_resolution_m",
                "boundary_basis")
    validated = []
    seen = set()
    for record in sources:
        if not isinstance(record, dict) or any(key not in record for key in required):
            raise ValueError("Source record missing required provenance fields")
        kind = record["constraint_type"]
        if not isinstance(kind, str) or not kind.strip() or kind in seen:
            raise ValueError("Source constraint_type must be unique and nonempty")
        seen.add(kind)
        for field in ("dataset_id", "source_url", "accessed_utc", "boundary_basis"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise ValueError(f"Invalid source {field}")
        parsed = urlparse(record["source_url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("Source URL must be HTTPS")
        try:
            accessed = datetime.fromisoformat(record["accessed_utc"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid source access timestamp") from exc
        if accessed.tzinfo is None or accessed.utcoffset() is None:
            raise ValueError("Source access timestamp requires timezone")
        if record["effective_date"] is not None:
            try:
                datetime.fromisoformat(record["effective_date"])
            except (ValueError, TypeError) as exc:
                raise ValueError("Invalid source effective date") from exc
        for field in ("horizontal_accuracy_m", "native_resolution_m"):
            value = record[field]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                      or not math.isfinite(value) or value <= 0):
                raise ValueError(f"Invalid source {field}")
        validated.append({key: record[key] for key in required})
    if seen != types:
        raise ValueError("Source register must cover exactly the reported constraint types")
    return sorted(validated, key=lambda item: item["constraint_type"])


def write_reports(rows: list[dict], directory: str | Path, sources: list[dict] | None = None) -> tuple[Path, Path]:
    """Write stable outputs; caller is responsible for access control and retention."""
    ordered = validate_rows(rows)
    if not ordered:
        raise ValueError("No screening rows to report")
    provenance = validate_sources(sources, {row["constraint_type"] for row in ordered}) if sources is not None else []
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "parcel_constraints.csv"
    json_path = output / "parcel_screening.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(ordered)
    payload = {
        "method": "synthetic_preliminary_parcel_screening_v1",
        "disclaimer": "Desktop GIS screening only; not a survey or regulatory determination.",
        "source_register": provenance,
        "provenance_status": "validated" if sources is not None else "not_provided",
        "rows": ordered,
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return csv_path, json_path
