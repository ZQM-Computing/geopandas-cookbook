"""Source resolution and boundary-review metadata for parcel GIS screening.

These are *review flags*, not spatial corrections or claims of surveyed accuracy.
"""
from __future__ import annotations

import math

import geopandas as gpd

REQUIRED = ("dataset_id", "source_url", "accessed_utc", "effective_date",
            "horizontal_accuracy_m", "native_resolution_m", "boundary_basis")


def validate_source_record(record: dict) -> dict:
    """Validate explicit source metadata; unknown accuracy stays unknown."""
    missing = [key for key in REQUIRED if key not in record]
    if missing:
        raise ValueError("Missing source metadata: " + ", ".join(missing))
    for key in ("dataset_id", "source_url", "accessed_utc", "boundary_basis"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    for key in ("horizontal_accuracy_m", "native_resolution_m"):
        value = record[key]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (float, int))
                                  or not math.isfinite(value) or value <= 0):
            raise ValueError(f"{key} must be a positive finite number or None")
    if record["effective_date"] is not None and not isinstance(record["effective_date"], str):
        raise ValueError("effective_date must be a string or None")
    return dict(record)


def boundary_review_flags(parcels: gpd.GeoDataFrame, constraints: gpd.GeoDataFrame,
                          tolerance_m: float) -> list[dict]:
    """Flag parcel boundaries near mapped constraints without altering geometry.

    A positive tolerance is an analyst-defined review distance, NOT the
    dataset's positional accuracy or a regulatory buffer.
    """
    if not math.isfinite(tolerance_m) or tolerance_m <= 0:
        raise ValueError("tolerance_m must be positive and finite")
    if parcels.crs is None or constraints.crs is None or parcels.crs != constraints.crs:
        raise ValueError("Matching projected CRS required")
    if not parcels.crs.is_projected or any(
        axis.unit_name.lower() not in ("metre", "meter", "metres", "meters")
        for axis in parcels.crs.axis_info[:2]
    ):
        raise ValueError("Projected metre CRS required")
    for name, frame, key in (("parcels", parcels, "parcel_id"), ("constraints", constraints, "constraint_type")):
        if key not in frame:
            raise ValueError(f"{name} missing {key}")
        if frame.geometry.isna().any() or frame.geometry.is_empty.any() or not frame.geometry.is_valid.all():
            raise ValueError(f"{name} has invalid geometry")
    flags = []
    for parcel_id, geometry in zip(parcels.parcel_id, parcels.geometry):
        for kind, constraint_geometry in zip(constraints.constraint_type, constraints.geometry):
            distance = geometry.boundary.distance(constraint_geometry)
            if distance <= tolerance_m:
                flags.append({"parcel_id": parcel_id, "constraint_type": kind,
                              "boundary_distance_m": distance, "review_tolerance_m": tolerance_m,
                              "flag": "boundary_proximity_review"})
    return flags
