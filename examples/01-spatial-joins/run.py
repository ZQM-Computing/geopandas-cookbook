"""Example 01: Spatial joins with GeoPandas."""

import geopandas as gpd
from shapely.geometry import Point, Polygon

# Create synthetic points
points = gpd.GeoDataFrame(
    {"name": ["A", "B", "C", "D", "E"]},
    geometry=[
        Point(-80.93, 29.02),
        Point(-80.92, 29.03),
        Point(-80.91, 29.01),
        Point(-80.94, 29.04),
        Point(-80.90, 29.00),
    ],
    crs="EPSG:4326",
)

# Create synthetic polygons
polygons = gpd.GeoDataFrame(
    {"zone": ["north", "south"]},
    geometry=[
        Polygon([(-80.95, 29.05), (-80.90, 29.05), (-80.90, 29.00), (-80.95, 29.00)]),
        Polygon([(-80.95, 29.00), (-80.90, 29.00), (-80.90, 28.95), (-80.95, 28.95)]),
    ],
    crs="EPSG:4326",
)

# Spatial join: point-in-polygon
joined = gpd.sjoin(points, polygons, how="left", predicate="within")
print("Point-in-polygon join:")
print(joined[["name", "zone"]])
print()

# Nearest join
nearest = gpd.sjoin_nearest(points, polygons, how="left")
print("Nearest join:")
print(nearest[["name", "zone"]])
