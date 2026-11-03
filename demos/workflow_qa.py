"""Synthetic point-data QA: explicit CRS, reconciled records, atomic report output."""

import argparse
from collections import Counter
import hashlib
import json
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


def build_report(raw):
    """Validate one JSON batch; return a deterministic, self-contained QA bundle.

    Batch contract failures raise ValueError. Record defects remain in the
    rejected list, with one entry per original row and possibly several reasons.
    """
    batch = json.loads(raw)
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


def run(input_path, output_path):
    """Publish a single JSON bundle only after the entire batch is processed."""
    input_path, output_path = Path(input_path), Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise ValueError("output must not overwrite input")
    report = build_report(input_path.read_bytes())
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
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
    args = parser.parse_args()
    result = run(args.input, args.output)
    print(json.dumps(result["summary"], sort_keys=True))
