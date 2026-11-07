"""Offline, model-agnostic GIS reasoning evaluation on synthetic questions.

This is a transparent smoke-test harness, NOT a blinded independent leaderboard.
No LLM calls, photo uploads, API keys, network access or real locations.
Usage:
  python demos/spatial_ai_arena.py --questions
  python demos/spatial_ai_arena.py --score path/to/predictions.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

TASKS = (
    {
        "id": "projected_rectangle_area",
        "prompt": "A rectangle in a metric projected CRS measures 100 m by 200 m. What is its area in square meters?",
        "answer_type": "number",
        "unit": "m2",
        "expected": 20000.0,
        "tolerance": 0.001,
    },
    {
        "id": "planar_distance",
        "prompt": "Two points in a suitable local projected CRS are (0,0) and (3,4) meters. What is their Euclidean distance in meters?",
        "answer_type": "number",
        "unit": "m",
        "expected": 5.0,
        "tolerance": 0.000001,
    },
    {
        "id": "polygon_boundary_covers",
        "prompt": "An axis-aligned square covers x=0..4 and y=0..4, boundaries inclusive. How many points (0,2), (4,4), (5,5), (1,1) are covered?",
        "answer_type": "number",
        "unit": "points",
        "expected": 3,
        "tolerance": 0,
    },
    {
        "id": "duplicate_spatial_join",
        "prompt": "Two sites have 1 and 2 matching hazard polygons, respectively. If the join retains every match, how many output rows result?",
        "answer_type": "number",
        "unit": "rows",
        "expected": 3,
        "tolerance": 0,
    },
    {
        "id": "geographic_crs_area",
        "prompt": "A polygon has EPSG:4326 coordinates in degrees. Choose the valid action before calculating area in square meters.",
        "answer_type": "choice",
        "unit": None,
        "expected": "reproject_to_suitable_equal_area_crs",
        "options": ("multiply_degrees_by_111000", "reproject_to_suitable_equal_area_crs", "treat_degrees_as_meters"),
    },
    {
        "id": "missing_raster_coverage",
        "prompt": "An imagery source has no coverage over a parcel. Choose the defensible conclusion for a land-change screening result.",
        "answer_type": "choice",
        "unit": None,
        "expected": "unknown_due_to_missing_coverage",
        "options": ("no_change_detected", "unknown_due_to_missing_coverage", "zero_risk"),
    },
)

_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_. -]{0,59}$")


def public_questions():
    """Expose only the task prompts and answer schemas; never expected values."""
    return [
        {k: task[k] for k in ("id", "prompt", "answer_type", "unit")}
        | ({"options": list(task["options"])} if "options" in task else {})
        for task in TASKS
    ]


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys are forbidden")
        result[key] = value
    return result


def load_submission(path: Path):
    """Read a bounded, strictly parsed public-safe JSON submission."""
    if path.stat().st_size > 128 * 1024:
        raise ValueError("Submission exceeds 128 KiB")
    raw = path.read_text(encoding="utf-8")
    data = json.loads(
        raw,
        object_pairs_hook=_unique_object,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON values are forbidden")),
    )
    if not isinstance(data, dict) or set(data) != {"run_label", "predictions"}:
        raise ValueError("Submission requires only run_label and predictions")
    if not isinstance(data["run_label"], str) or not _LABEL_RE.fullmatch(data["run_label"]):
        raise ValueError("run_label must be a short, non-sensitive identifier")
    if not isinstance(data["predictions"], list) or len(data["predictions"]) > len(TASKS):
        raise ValueError("predictions must be a bounded array")
    return data


def evaluate(submission):
    """Score a synthetic sample, including omitted tasks as unanswered."""
    if not isinstance(submission, dict) or set(submission) != {"run_label", "predictions"}:
        raise ValueError("Invalid submission shape")
    label = submission["run_label"]
    if not isinstance(label, str) or not _LABEL_RE.fullmatch(label):
        raise ValueError("Invalid run_label")
    predictions = submission["predictions"]
    if not isinstance(predictions, list) or len(predictions) > len(TASKS):
        raise ValueError("Invalid predictions")
    known = {task["id"]: task for task in TASKS}
    got = {}
    for entry in predictions:
        if not isinstance(entry, dict) or set(entry) != {"task_id", "answer"}:
            raise ValueError("Prediction must contain only task_id and answer")
        key = entry["task_id"]
        if not isinstance(key, str) or key not in known or key in got:
            raise ValueError("Unknown or duplicate task_id")
        value = entry["answer"]
        task = known[key]
        if task["answer_type"] == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Numerical answers must be finite numbers")
        elif not isinstance(value, str) or len(value) > 128:
            raise ValueError("Choice answers must be short strings")
        got[key] = value

    details = []
    for task in TASKS:
        key = task["id"]
        if key not in got:
            details.append({"task_id": key, "status": "unanswered"})
            continue
        answer = got[key]
        if task["answer_type"] == "number":
            correct = abs(answer - task["expected"]) <= task["tolerance"]
        else:
            correct = answer == task["expected"]
        details.append({"task_id": key, "status": "passed" if correct else "failed"})
    passed = sum(result["status"] == "passed" for result in details)
    total = len(TASKS)
    return {
        "run_label": label,
        "benchmark": "ZQM synthetic GIS reasoning sanity checks v1",
        "independent_benchmark": False,
        "total": total,
        "attempted": len(got),
        "passed": passed,
        "score_percent": round(100 * passed / total, 2),
        "complete": len(got) == total,
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--questions", action="store_true")
    group.add_argument("--score", type=Path)
    args = parser.parse_args()
    try:
        output = public_questions() if args.questions else evaluate(load_submission(args.score))
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(output, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
