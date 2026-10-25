"""Point-in-polygon and nearest-neighbour joins using synthetic data."""
import geopandas as gpd
from shapely.geometry import Point, box

zones = gpd.GeoDataFrame(
    {"zone": ["west", "east"]},
    geometry=[box(-81.2, 29.1, -81.0, 29.3), box(-81.0, 29.1, -80.8, 29.3)],
    crs="EPSG:4326",
)
points = gpd.GeoDataFrame(
    {"asset_id": [1, 2, 3], "kind": ["school", "clinic", "library"]},
    geometry=[Point(-81.1, 29.2), Point(-80.9, 29.2), Point(-80.85, 29.25)],
    crs="EPSG:4326",
)
joined = gpd.sjoin(points, zones, how="left", predicate="within")
print("Point-in-polygon results:")
print(joined[["asset_id", "kind", "zone"]].to_string(index=False))

# Distances must be calculated in a projected CRS, not longitude/latitude degrees.
facilities = gpd.GeoDataFrame(
    {"facility": ["west hub", "east hub"]},
    geometry=[Point(-81.15, 29.2), Point(-80.88, 29.2)],
    crs="EPSG:4326",
).to_crs("EPSG:32617")
projected_points = points.to_crs("EPSG:32617")
nearest = gpd.sjoin_nearest(projected_points, facilities, distance_col="distance_m")
print("\nNearest facilities (metres):")
print(nearest[["asset_id", "facility", "distance_m"]].round({"distance_m": 1}).to_string(index=False))
