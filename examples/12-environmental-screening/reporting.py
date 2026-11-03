"""Deterministic parcel-level CSV and JSON report generation from synthetic screening.

No automatic fetches, no geocoding, and no regulatory conclusions.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

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
        validated.append({name: row[name] for name in FIELDS})
    return sorted(validated, key=lambda row: (row["parcel_id"], row["constraint_type"]))


def write_reports(rows: list[dict], directory: str | Path, sources: list[dict] | None = None) -> tuple[Path, Path]:
    """Write stable outputs; caller is responsible for access control and retention."""
    ordered = validate_rows(rows)
    if not ordered:
        raise ValueError("No screening rows to report")
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
        "source_register": sources if sources is not None else [],
        "rows": ordered,
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return csv_path, json_path
