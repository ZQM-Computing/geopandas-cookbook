"""Deterministic checks for the illustrative GIS reasoning scorer."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "demos" / "spatial_ai_arena.py"
spec = importlib.util.spec_from_file_location("spatial_ai_arena", MODULE)
arena = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arena)


def test_questions_do_not_publish_gold_answers():
    public = arena.public_questions()
    assert len(public) == 6
    assert len({task["id"] for task in public}) == 6
    assert all("expected" not in task and "tolerance" not in task for task in public)
    assert all("prompt" in task and "answer_type" in task for task in public)


def test_full_submission_scores_correctly_and_labels_itself_not_independent():
    predictions = [
        {"task_id": task["id"], "answer": task["expected"]}
        for task in arena.TASKS
    ]
    report = arena.evaluate({"run_label": "local-fixture", "predictions": predictions})
    assert report["total"] == 6
    assert report["attempted"] == report["passed"] == 6
    assert report["score_percent"] == 100
    assert report["complete"] is True
    assert report["independent_benchmark"] is False
    assert all(item["status"] == "passed" for item in report["details"])
    assert "expected" not in json.dumps(report)


def test_missing_and_wrong_answers_are_reported_not_ignored():
    report = arena.evaluate({
        "run_label": "bad-fixture",
        "predictions": [
            {"task_id": "projected_rectangle_area", "answer": 20},
            {"task_id": "missing_raster_coverage", "answer": "no_change_detected"},
        ],
    })
    assert report["attempted"] == 2
    assert report["passed"] == 0
    assert report["score_percent"] == 0.0
    assert report["complete"] is False
    assert {x["status"] for x in report["details"]} == {"failed", "unanswered"}


@pytest.mark.parametrize("predictions", [
    [{"task_id": "unknown", "answer": 1}],
    [{"task_id": "planar_distance", "answer": 5}, {"task_id": "planar_distance", "answer": 5}],
    [{"task_id": "planar_distance", "answer": True}],
    [{"task_id": "planar_distance", "answer": float("nan")}],
    [{"task_id": "planar_distance", "answer": "5"}],
    [{"task_id": "geographic_crs_area", "answer": 20}],
    [{"task_id": "planar_distance", "answer": 5, "private_url": "https://example.com"}],
])
def test_reject_invalid_or_ambiguous_predictions(predictions):
    with pytest.raises(ValueError):
        arena.evaluate({"run_label": "fixture-1", "predictions": predictions})


def test_reject_duplicate_json_fields_and_non_finite_values(tmp_path):
    for text in (
        '{"run_label":"x","run_label":"y","predictions":[]}',
        '{"run_label":"x","predictions":[{"task_id":"planar_distance","answer":NaN}]}',
    ):
        file = tmp_path / "submission.json"
        file.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            arena.load_submission(file)


def test_cli_public_questions_and_score_are_machine_readable(tmp_path):
    output = subprocess.run([sys.executable, str(MODULE), "--questions"], text=True, capture_output=True)
    assert output.returncode == 0, output.stderr
    assert "expected" not in output.stdout
    path = tmp_path / "answers.json"
    path.write_text(json.dumps({"run_label": "manual", "predictions": []}), encoding="utf-8")
    scored = subprocess.run(
        [sys.executable, str(MODULE), "--score", str(path)], text=True, capture_output=True
    )
    assert scored.returncode == 0, scored.stderr
    assert json.loads(scored.stdout)["attempted"] == 0
