"""Example 06: Performance tips for GeoPandas."""

import time

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

# Create large synthetic dataset
n = 10000
np.random.seed(42)
lons = np.random.uniform(-80.95, -80.90, n)
lats = np.random.uniform(28.95, 29.05, n)
points = gpd.GeoDataFrame(
    {"value": np.random.randint(1, 100, n)}, geometry=gpd.points_from_xy(lons, lats), crs="EPSG:4326"
)
print(f"Created {len(points)} points")

# Slow: row-wise iteration
start = time.time()
count = 0
for idx, row in points.iterrows():
    if row["value"] > 50:
        count += 1
print(f"Row-wise iteration: {time.time() - start:.3f}s (count={count})")

# Fast: vectorized operations
start = time.time()
count_fast = (points["value"] > 50).sum()
print(f"Vectorized: {time.time() - start:.3f}s (count={count_fast})")

# Fast: spatial index
polygons = gpd.GeoDataFrame(
    {"zone": ["all"]},
    geometry=[Polygon([(-80.95, 29.05), (-80.90, 29.05), (-80.90, 28.95), (-80.95, 28.95)])],
    crs="EPSG:4326",
)
start = time.time()
joined = gpd.sjoin(points, polygons, how="inner", predicate="within")
print(f"Spatial join with index: {time.time() - start:.3f}s (matched={len(joined)})")
