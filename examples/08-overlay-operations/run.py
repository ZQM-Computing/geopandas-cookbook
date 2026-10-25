"""Demonstrate intersection, union, difference, and symmetric difference."""
import geopandas as gpd
from shapely.geometry import box

left = gpd.GeoDataFrame({"left_id": [1]}, geometry=[box(0, 0, 3, 3)], crs="EPSG:3857")
right = gpd.GeoDataFrame({"right_id": [1]}, geometry=[box(2, 1, 4, 4)], crs="EPSG:3857")
for operation in ("intersection", "union", "difference", "symmetric_difference"):
    result = gpd.overlay(left, right, how=operation, keep_geom_type=False)
    print(f"{operation}: {len(result)} feature(s), total area={result.geometry.area.sum():.1f} m²")
assert abs(gpd.overlay(left, right, how="intersection").geometry.area.sum() - 2.0) < 1e-9
