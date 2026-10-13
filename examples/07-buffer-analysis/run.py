#!/usr/bin/env python3
"""Example 07: Buffer analysis and proximity."""
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd
import numpy as np

# Create synthetic facilities and population points
np.random.seed(42)
facilities = gpd.GeoDataFrame(
    {"name": ["Hospital", "School", "Fire Station", "Library"], "type": ["health", "edu", "safety", "civic"]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01), Point(-80.90, 29.00)],
    crs="EPSG:4326"
)

# Create population points
pop_points = gpd.GeoDataFrame(
    {"population": np.random.randint(50, 500, 20)},
    geometry=gpd.points_from_xy(
        np.random.uniform(-80.94, -80.89, 20),
        np.random.uniform(28.99, 29.04, 20)
    ),
    crs="EPSG:4326"
)

# Buffer facilities by service area (in degrees, approximate)
facilities["buffer_1km"] = facilities.geometry.buffer(0.01)  # ~1km at this latitude
facilities["buffer_5km"] = facilities.geometry.buffer(0.05)  # ~5km

# Find population within 1km of each facility
print("=== Population within 1km of facilities ===")
for idx, fac in facilities.iterrows():
    within = pop_points[pop_points.geometry.within(fac["buffer_1km"])]
    total_pop = within["population"].sum()
    print(f"  {fac['name']}: {len(within)} points, population={total_pop}")

# Service area overlap analysis
print("\n=== Service area overlap ===")
for i in range(len(facilities)):
    for j in range(i+1, len(facilities)):
        f1 = facilities.iloc[i]
        f2 = facilities.iloc[j]
        overlap = f1["buffer_5km"].intersection(f2["buffer_5km"])
        if not overlap.is_empty:
            print(f"  {f1['name']} and {f2['name']} 5km buffers overlap")
