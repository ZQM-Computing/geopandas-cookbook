"""Transform features through a projected analysis CRS and back to CRS84."""
import geopandas as gpd
from shapely.geometry import Point

source = gpd.GeoDataFrame(
    {"asset_id": [1, 2], "label": ["west", "east"]},
    geometry=[Point(-81.1, 29.2), Point(-80.9, 29.25)],
    crs="OGC:CRS84",
)
utm = source.to_crs("EPSG:32617")
albers = utm.to_crs("EPSG:5070")
round_trip = albers.to_crs("OGC:CRS84")
drift = source.geometry.distance(round_trip.geometry).max()
print("UTM coordinates:")
print(utm[["asset_id", "geometry"]].to_string(index=False))
print(f"Albers projected area is available in CRS {albers.crs.to_string()}")
print(f"Round-trip coordinate-space drift: {drift:.10f} degrees")
assert drift < 1e-8
