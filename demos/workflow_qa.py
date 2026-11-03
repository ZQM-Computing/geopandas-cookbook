"""Synthetic point-data QA: explicit CRS, reconciled records, atomic report output."""

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import tempfile

import geopandas as gpd
import numpy as np
import pyproj
import shapely
from shapely import from_wkt
from shapely.geometry import mapping


def _unique_object(pairs):
    """Reject ambiguous object fields at every nesting level."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field names are not permitted")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite JSON numbers are not permitted")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON number exceeds finite floating-point range")
    return number


def build_report(raw):
    """Validate one JSON batch; return a deterministic, self-contained QA bundle.

    Batch contract failures raise ValueError. Record defects remain in the
    rejected list, with one entry per original row and possibly several reasons.
    """
    batch = json.loads(raw, object_pairs_hook=_unique_object,
                       parse_constant=_reject_constant, parse_float=_finite_float)
    if not isinstance(batch, dict):
        raise ValueError("batch must be an object")
    for field in ("source_crs", "analysis_crs", "boundary_wkt", "records"):
        if field not in batch:
            raise ValueError(f"missing batch field: {field}")
    if not isinstance(batch["records"], list) or not batch["records"]:
        raise ValueError("records must be a nonempty list")
    for key in ("source_crs", "analysis_crs"):
        if not isinstance(batch[key], str) or not batch[key].strip():
            raise ValueError(f"{key} must be explicitly declared")
    try:
        source = pyproj.CRS(batch["source_crs"])
        target = pyproj.CRS(batch["analysis_crs"])
    except pyproj.exceptions.CRSError as exc:
        raise ValueError("source_crs and analysis_crs must be valid coordinate systems") from exc
    if not target.is_projected:
        raise ValueError("analysis_crs must be projected")
    if not isinstance(batch["boundary_wkt"], str):
        raise ValueError("boundary_wkt must be a WKT string")
    try:
        boundary = from_wkt(batch["boundary_wkt"])
    except shapely.errors.GEOSException as exc:
        raise ValueError("boundary must be a valid finite polygon") from exc
    if (boundary is None or boundary.is_empty or not boundary.is_valid
            or boundary.geom_type not in ("Polygon", "MultiPolygon")
            or not np.isfinite(shapely.get_coordinates(boundary)).all()):
        raise ValueError("boundary must be a valid finite polygon")
    boundary = gpd.GeoSeries([boundary], crs=source).to_crs(target).iloc[0]
    if not boundary.is_valid or not np.isfinite(shapely.get_coordinates(boundary)).all():
        raise ValueError("boundary cannot be transformed to analysis_crs")
    records = batch["records"]
    if any(not isinstance(row, dict) for row in records):
        raise ValueError("each record must be an object")
    ids = [r.get("record_id") for r in records]
    counts = Counter(x for x in ids if isinstance(x, str))
    accepted, rejected = [], []
    for position, row in enumerate(records):
        reasons = []
        record_id = row.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            reasons.append("missing_or_invalid_id")
        elif counts[record_id] > 1:
            reasons.append("duplicate_id")
        name = row.get("name")
        if not isinstance(name, str) or not name.strip():
            reasons.append("missing_name")
        wkt = row.get("wkt")
        geom = None
        if isinstance(wkt, str):
            try:
                geom = from_wkt(wkt)
            except (shapely.errors.GEOSException, TypeError, ValueError):
                pass
        if geom is None or geom.is_empty:
            reasons.append("missing_or_unreadable_geometry")
        elif geom.geom_type != "Point":
            reasons.append("not_point")
        elif geom.has_z or getattr(geom, "has_m", False):
            reasons.append("not_2d")
        elif not geom.is_valid or not np.isfinite(shapely.get_coordinates(geom)).all():
            reasons.append("invalid_geometry")
        else:
            geom = gpd.GeoSeries([geom], crs=source).to_crs(target).iloc[0]
            if not geom.is_valid or not np.isfinite(shapely.get_coordinates(geom)).all():
                reasons.append("untransformable_geometry")
            elif not boundary.covers(geom):
                reasons.append("outside_boundary")
        if reasons:
            rejected.append({"row": position, "record": row, "reasons": reasons})
        else:
            accepted.append({"type": "Feature", "geometry": mapping(geom),
                             "properties": {"record_id": record_id, "name": name}})
    return {
        "schema_version": 1,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "source_crs": source.to_string(), "analysis_crs": target.to_string(),
        "boundary_rule": "covers: includes points on the boundary",
        "versions": {"python": platform.python_version(), "geopandas": gpd.__version__,
                     "shapely": shapely.__version__, "pyproj": pyproj.__version__},
        "summary": {"input": len(records), "accepted": len(accepted), "rejected": len(rejected)},
        "accepted": accepted, "rejected": rejected,
    }


def render_summary(report):
    """Render a buyer-readable summary without source records or coordinates.

    The input hash and software versions identify the evidence. Reasons count
    affected rows, so their total can exceed the rejected-row count.
    """
    summary = report["summary"]
    reasons = Counter(reason for row in report["rejected"] for reason in set(row["reasons"]))
    decision = ("Review required: rejected records need correction or an agreed disposition."
                if summary["rejected"] else
                "No records rejected by the configured checks; owner review is still required.")
    lines = [
        "# GIS workflow QA summary", "", decision, "",
        "| Input records | Accepted records | Rejected records |",
        "| --- | --- | --- |",
        f"| {summary['input']} | {summary['accepted']} | {summary['rejected']} |", "",
        "Every input row is accounted for once as accepted or rejected.", "",
        "## Findings", "",
    ]
    if reasons:
        lines += ["| Rejection reason | Affected records |", "| --- | --- |"]
        lines += [f"| {reason} | {count} |" for reason, count in sorted(reasons.items())]
        lines += ["", "A record may have multiple reasons; these counts are not additive."]
    else:
        lines += ["No rejection reasons were recorded."]
    source_epsg = pyproj.CRS(report["source_crs"]).to_epsg()
    analysis_epsg = pyproj.CRS(report["analysis_crs"]).to_epsg()
    lines += [
        "", "## Evidence", "",
        f"- Input SHA-256: `{report['input_sha256']}`",
        f"- Bundle schema version: {report['schema_version']}",
        f"- Source CRS: {'EPSG:' + str(source_epsg) if source_epsg else 'custom; see JSON bundle'}",
        f"- Analysis CRS: {'EPSG:' + str(analysis_epsg) if analysis_epsg else 'custom; see JSON bundle'}",
        "- Boundary rule: covers, including points on the boundary.",
    ]
    lines += [f"- {name}: {version}" for name, version in sorted(report["versions"].items())]
    lines += [
        "", "## Interpretation and next step", "",
        "This report summarizes configured data checks. It does not establish source",
        "accuracy, regulatory suitability, production readiness, or measured labor savings.",
        "The bundled example uses synthetic data. For other inputs, document their",
        "provenance separately before using the results in a client deliverable.", "",
        "Agree on rejection handling, acceptance thresholds, and the responsible reviewer",
        "before importing accepted records. Refer to the JSON bundle for row-level details.",
        "Raw records, names, IDs and coordinates are omitted from this summary; counts,",
        "CRS, versions and the input hash remain. Review them before external sharing.", "",
    ]
    return "\n".join(lines)


def run(input_path, output_path, output_format="json"):
    """Publish one JSON bundle or Markdown summary after processing the batch."""
    input_path, output_path = Path(input_path), Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise ValueError("output must not overwrite input")
    if output_format not in ("json", "markdown"):
        raise ValueError("output_format must be json or markdown")
    report = build_report(input_path.read_bytes())
    # Enforce the same strict JSON evidence contract for both output formats.
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if output_format == "markdown":
        payload = render_summary(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    staged = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output_path.parent,
                                         prefix=".qa-", delete=False) as stream:
            staged = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staged, output_path)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json",
                        help="JSON evidence bundle (default) or summary without raw records")
    args = parser.parse_args()
    result = run(args.input, args.output, args.format)
    print(json.dumps(result["summary"], sort_keys=True))
