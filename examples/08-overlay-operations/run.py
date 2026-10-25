"""Demonstrate intersection, union, difference, and symmetric difference."""
import geopandas as gpd
from shapely.geometry import box

left = gpd.GeoDataFrame({"left_id": [1]}, geometry=[box(0, 0, 3, 3)], crs="EPSG:3857")
right = gpd.GeoDataFrame({"right_id": [1]}, geometry=[box(2, 1, 4, 4)], crs="EPSG:3857")
areas = {}
for operation in ("intersection", "union", "difference", "symmetric_difference"):
    result = gpd.overlay(left, right, how=operation, keep_geom_type=False)
    areas[operation] = float(result.geometry.area.sum())
    print(f"{operation}: {len(result)} feature(s), total area={areas[operation]:.1f} m²")

# Fixture geometry: left=9, right=6, overlap=2, union=9+6-2=13.
expected_areas = {
    "intersection": 2.0,
    "union": 13.0,
    "difference": 7.0,
    "symmetric_difference": 11.0,
}
for operation, expected in expected_areas.items():
    assert abs(areas[operation] - expected) < 1e-9, (
        f"{operation} area changed: expected {expected}, got {areas[operation]}"
    )
assert abs(areas["union"] + areas["intersection"] - 15.0) < 1e-9
