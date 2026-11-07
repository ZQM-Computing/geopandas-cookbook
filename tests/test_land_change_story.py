"""Regression checks for the reusable synthetic visual storytelling demo."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "land_change_story", ROOT / "demos" / "land_change_story.py"
)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_scenes_are_valid_and_metrics_reconcile():
    first, second = module.make_scenes()
    assert first.is_valid and second.is_valid
    stats = module.change_metrics(first, second)
    assert stats["scenario_a_area"] == 12
    assert stats["scenario_b_area"] == 23
    assert stats["gross_gain_area"] == 11
    assert stats["gross_loss_area"] == 0
    assert stats["net_change_area"] == (
        stats["gross_gain_area"] - stats["gross_loss_area"]
    )
    assert stats["dataset"] == "SYNTHETIC_DEMONSTRATION_ONLY"
    assert stats["coordinate_system"] == "dimensionless_planar_grid_no_real_crs"


def test_output_contains_visual_and_companion_evidence(tmp_path):
    result = module.run(tmp_path)
    image = tmp_path / "synthetic-land-change.png"
    record = tmp_path / "synthetic-land-change.metrics.json"
    assert image.exists() and image.stat().st_size > 1000
    assert json.loads(record.read_text(encoding="utf-8")) == result
    assert result == module.run(tmp_path)  # deterministic numerical output


def test_rejects_outside_study_area():
    from shapely.geometry import box
    before, _ = module.make_scenes()
    try:
        module.change_metrics(before, box(0, 0, 11, 11))
    except ValueError as exc:
        assert "outside synthetic study boundary" in str(exc)
    else:
        raise AssertionError("Study coverage failure went undetected")
