"""Assign every demand point to its nearest facility and summarize coverage."""
import geopandas as gpd
from shapely.geometry import Point

facilities = gpd.GeoDataFrame(
    {"facility_id": [101, 102, 103], "facility": ["North", "Central", "South"]},
    geometry=[Point(-81.1, 29.35), Point(-81.0, 29.2), Point(-80.9, 29.05)],
    crs="EPSG:4326",
).to_crs("EPSG:32617")
demand = gpd.GeoDataFrame(
    {"demand_id": range(1, 8)},
    geometry=[Point(-81.12, 29.33), Point(-81.08, 29.3), Point(-81.02, 29.22),
              Point(-80.98, 29.18), Point(-80.92, 29.08), Point(-80.88, 29.04),
              Point(-81.3, 29.2)],
    crs="EPSG:4326",
).to_crs("EPSG:32617")
assigned = gpd.sjoin_nearest(demand, facilities, distance_col="distance_m")
print(assigned[["demand_id", "facility", "distance_m"]].round({"distance_m": 1}).to_string(index=False))
print("\nAssignments per facility:")
print(assigned.groupby("facility")["demand_id"].count().to_string())
