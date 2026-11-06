"""Create a reviewer map from synthetic parcel and constraint geometries.

A figure is a visual aid, not a surveyed boundary or regulatory determination.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_review_map(parcels: gpd.GeoDataFrame, constraints: gpd.GeoDataFrame,
                      coverage: gpd.GeoDataFrame, destination: str | Path,
                      *, title: str = "Synthetic parcel environmental screening example") -> Path:
    """Render an offline, deterministic PNG with legend and explicit uncertainty note."""
    if parcels.empty:
        raise ValueError("At least one parcel is required")
    if parcels.crs is None or constraints.crs != parcels.crs or coverage.crs != parcels.crs:
        raise ValueError("All layers require matching CRS")
    if not parcels.crs.is_projected:
        raise ValueError("Projected CRS required for review map")
    if not all(frame.geometry.is_valid.all() and not frame.geometry.isna().any()
               for frame in (parcels, constraints, coverage)):
        raise ValueError("All geometries must be valid and non-null")
    path = Path(destination)
    if path.suffix.lower() != ".png":
        raise ValueError("Review map destination must be PNG")
    if path.exists():
        raise FileExistsError("Refusing to overwrite existing review map")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 7), dpi=150)
    try:
        if not coverage.empty:
            coverage.plot(ax=ax, facecolor="#b5d8e8", edgecolor="none",
                          alpha=0.45, label="Source coverage")
        if not constraints.empty:
            constraints.plot(ax=ax, facecolor="#db8556", edgecolor="#8d402a",
                             alpha=0.65, label="Mapped constraints")
        parcels.boundary.plot(ax=ax, color="#20252a", linewidth=1.4,
                              label="Parcel boundaries (GIS)")
        if "parcel_id" in parcels:
            for parcel_id, geometry in zip(parcels.parcel_id, parcels.geometry):
                point = geometry.representative_point()
                ax.text(point.x, point.y, str(parcel_id), ha="center", va="center",
                        parse_math=False, zorder=5,
                        bbox={"facecolor": "white", "edgecolor": "#20252a", "alpha": 0.9})
        # Regional source extents must not shrink parcel detail to a pixel.
        # These are view limits only; screening/export geometries stay intact.
        left, bottom, right, top = parcels.total_bounds
        padding = max(right - left, top - bottom) * 0.08
        if padding == 0:
            padding = 1.0
        ax.set_xlim(left - padding, right + padding)
        ax.set_ylim(bottom - padding, top + padding)
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_xlabel(f"Projected X ({parcels.crs.axis_info[0].unit_name})")
        ax.set_ylabel(f"Projected Y ({parcels.crs.axis_info[1].unit_name})")
        # Explicit legend handles are more reliable than GeoPandas plot labels.
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        ax.legend(handles=[
            Patch(facecolor="#b5d8e8", alpha=0.45, label="Source coverage"),
            Patch(facecolor="#db8556", alpha=0.65, label="Mapped constraints"),
            Line2D([0], [0], color="#20252a", lw=1.4, label="Parcel boundaries (GIS)"),
        ], loc="upper right")
        fig.text(0.5, 0.015,
                 "Preliminary GIS screening only. Boundaries and mapped constraints may be incomplete or inaccurate.\n"
                 "Not a survey, wetland delineation, engineering opinion, or regulatory approval.\n"
                 "Coverage is source-specific; use the parcel matrix for each constraint type.",
                 ha="center", va="bottom", fontsize=8)
        fig.tight_layout(rect=(0, 0.1, 1, 1))
        fig.savefig(path, metadata={"Software": "ZQM Computing GeoPandas Cookbook"})
    finally:
        plt.close(fig)
    return path
