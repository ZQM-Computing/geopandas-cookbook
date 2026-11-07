"""Reproducible before/after communication example on purely synthetic planar shapes.

No satellite data, parcels, actual dates, real locations, or customer records.
Run: python demos/land_change_story.py --output-dir /tmp/zqm-land-change
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely import union_all
from shapely.geometry import box

STUDY_AREA = box(0, 0, 10, 10)


def make_scenes():
    """Return two synthetic, valid land-cover geometries in a dimensionless grid."""
    before = union_all([box(1, 1, 3, 5), box(7, 6, 9, 8)])
    after = union_all([before, box(3, 2, 6, 5), box(6, 6, 7, 8)])
    if not before.is_valid or not after.is_valid:
        raise ValueError("Synthetic source geometry is invalid")
    return before, after


def change_metrics(before, after):
    """Measure gross gain and loss; do not confuse net change with gross change."""
    if not (before.is_valid and after.is_valid):
        raise ValueError("Invalid source geometries")
    if not (STUDY_AREA.covers(before) and STUDY_AREA.covers(after)):
        raise ValueError("Geometry outside synthetic study boundary")
    gained = after.difference(before)
    lost = before.difference(after)
    return {
        "dataset": "SYNTHETIC_DEMONSTRATION_ONLY",
        "coordinate_system": "dimensionless_planar_grid_no_real_crs",
        "area_units": "square_grid_units",
        "scenario_a_area": before.area,
        "scenario_b_area": after.area,
        "gross_gain_area": gained.area,
        "gross_loss_area": lost.area,
        "net_change_area": after.area - before.area,
        "method": "Shapely topological difference; no imagery or observed changes",
    }


def render(before, after, destination: Path):
    """Export side-by-side figures with explicitly illustrative titles."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), layout="constrained")
    for axis, scene, title in zip(
        axes, (before, after), ("Scenario A · synthetic", "Scenario B · synthetic")
    ):
        gpd.GeoSeries([STUDY_AREA]).boundary.plot(ax=axis, color="#64748b", linewidth=2)
        gpd.GeoSeries([scene]).plot(ax=axis, color="#2563eb", edgecolor="#0f172a")
        axis.set(xlim=(-0.5, 10.5), ylim=(-0.5, 10.5), aspect="equal",
                 xlabel="Synthetic x", ylabel="Synthetic y", title=title)
        axis.grid(alpha=0.16)
    fig.suptitle("Illustrative land-cover difference — NOT observed Earth change")
    fig.savefig(destination, dpi=160, bbox_inches="tight")
    plt.close(fig)



def render_social(before, after, metrics, destination: Path):
    """Render an exact 1080x1920 vertical card on the same synthetic evidence."""
    if metrics.get("dataset") != "SYNTHETIC_DEMONSTRATION_ONLY":
        raise ValueError("Social render requires explicit synthetic provenance")
    figure = plt.figure(figsize=(9, 16), dpi=120, facecolor="#091a2e")
    try:
        figure.text(0.08, 0.955, "ZQM COMPUTING / GIS STORY", color="#a9cbe0",
                    fontsize=19, weight="bold")
        figure.text(0.08, 0.907, "WHAT CHANGED?", color="white",
                    fontsize=37, weight="bold")
        figure.text(0.08, 0.873, "Two illustrative coverage scenarios",
                    color="#cbd9e9", fontsize=19)

        scenes = [
            (before, "SCENARIO A", metrics["scenario_a_area"]),
            (after, "SCENARIO B", metrics["scenario_b_area"]),
        ]
        for index, (geometry, label, area) in enumerate(scenes):
            axis = figure.add_axes((0.10, 0.535 - index * 0.30, 0.80, 0.255))
            axis.set_facecolor("#eef4fb")
            gpd.GeoSeries([STUDY_AREA]).boundary.plot(ax=axis, color="#61748a", linewidth=2)
            gpd.GeoSeries([geometry]).plot(ax=axis, color="#2387b5", edgecolor="#123047")
            axis.set_xlim(-0.5, 10.5)
            axis.set_ylim(-0.5, 10.5)
            axis.set_aspect("equal")
            axis.set_axis_off()
            axis.text(0.035, 0.96, label, ha="left", va="top", transform=axis.transAxes,
                      fontsize=18, color="#0e293d", weight="bold")
            axis.text(0.035, 0.08, f"{area:g} square grid units", ha="left", va="bottom",
                      transform=axis.transAxes, fontsize=14, color="#0e293d")

        figure.text(0.08, 0.166, f"NET CHANGE: {metrics['net_change_area']:+g}",
                    color="#89e4c0", fontsize=28, weight="bold")
        figure.text(0.08, 0.132, "square grid units · synthetic topological difference",
                    color="#d2e0ee", fontsize=15)
        figure.text(0.08, 0.077, "ILLUSTRATIVE ONLY — NOT OBSERVED EARTH CHANGE",
                    color="#ffffff", fontsize=16, weight="bold")
        figure.text(0.08, 0.052, "Source and method: synthetic-land-change.metrics.json",
                    color="#b3c7d8", fontsize=12)
        figure.savefig(destination, dpi=120, facecolor=figure.get_facecolor())
    finally:
        plt.close(figure)



def run(output_dir: Path):
    """Write a visual and its auditable numerical companion."""
    before, after = make_scenes()
    metrics = change_metrics(before, after)
    output_dir.mkdir(parents=True, exist_ok=True)
    render(before, after, output_dir / "synthetic-land-change.png")
    render_social(before, after, metrics, output_dir / "synthetic-land-change-social.png")
    (output_dir / "synthetic-land-change.metrics.json").write_text(
        json.dumps(metrics, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Existing or new folder for PNG and metrics JSON")
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
