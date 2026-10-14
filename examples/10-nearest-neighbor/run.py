"""Example 10: Nearest neighbor analysis."""

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

# Create facilities and demand points
np.random.seed(42)
facilities = gpd.GeoDataFrame(
    {"name": ["Hospital A", "Hospital B", "Clinic C"]},
    geometry=[Point(-80.93, 29.02), Point(-80.91, 29.01), Point(-80.90, 29.00)],
    crs="EPSG:4326",
)

demand = gpd.GeoDataFrame(
    {"demand": np.random.randint(10, 100, 50)},
    geometry=gpd.points_from_xy(np.random.uniform(-80.94, -80.89, 50), np.random.uniform(28.99, 29.04, 50)),
    crs="EPSG:4326",
)

# Find nearest facility for each demand point (pure numpy)
fac_coords = np.array([(geom.x, geom.y) for geom in facilities.geometry])
demand_coords = np.array([(geom.x, geom.y) for geom in demand.geometry])

# Calculate distances (vectorized)
diffs = demand_coords[:, np.newaxis, :] - fac_coords[np.newaxis, :, :]
dists_all = np.sqrt(np.sum(diffs**2, axis=2))
idxs = np.argmin(dists_all, axis=1)
dists = np.min(dists_all, axis=1)

demand["nearest_facility"] = facilities.iloc[idxs]["name"].values
demand["distance_deg"] = dists

# Convert to approximate km (at this latitude)
demand["distance_km"] = dists * 111

print("=== Nearest facility analysis ===")
summary = demand.groupby("nearest_facility").agg(
    demand_points=("demand", "count"),
    total_demand=("demand", "sum"),
    avg_distance_km=("distance_km", "mean"),
    max_distance_km=("distance_km", "max"),
)
print(summary)

# Coverage analysis: demand within 2km of any facility
within_2km = demand[demand["distance_km"] <= 2]
print(f"\nDemand within 2km of facility: {len(within_2km)} points ({len(within_2km) / len(demand) * 100:.1f}%)")
print(f"Total demand within 2km: {within_2km['demand'].sum()}")
