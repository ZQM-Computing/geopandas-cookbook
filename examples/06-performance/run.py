"""Compare indexed and vectorized point-in-polygon filtering on synthetic data."""
import time

import geopandas as gpd
import numpy as np
from shapely.geometry import Point, box

rng = np.random.default_rng(20261024)
count = 20_000
xs = rng.uniform(-81.4, -80.7, count)
ys = rng.uniform(28.9, 29.6, count)
points = gpd.GeoSeries([Point(x, y) for x, y in zip(xs, ys)], crs="EPSG:4326")
area = box(-81.2, 29.1, -80.9, 29.4)

start = time.perf_counter()
indexed_positions = points.sindex.query(area, predicate="contains")
indexed_seconds = time.perf_counter() - start
start = time.perf_counter()
mask = points.within(area)
vectorized_count = int(mask.sum())
vectorized_seconds = time.perf_counter() - start
assert len(indexed_positions) == vectorized_count
print(f"Features: {count:,}")
print(f"Indexed query: {len(indexed_positions):,} matches in {indexed_seconds:.4f}s")
print(f"Vectorized scan: {vectorized_count:,} matches in {vectorized_seconds:.4f}s")
