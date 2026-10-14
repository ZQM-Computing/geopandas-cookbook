"""Example 11: CRS transformation pipeline."""

import geopandas as gpd
from shapely.geometry import Point, Polygon

# Create data in WGS84
data = gpd.GeoDataFrame(
    {"name": ["A", "B", "C"]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01)],
    crs="EPSG:4326",
)

print("=== CRS Transformation Pipeline ===")
print(f"Original CRS: {data.crs}")
print(data)
print()

# Transform to UTM Zone 17N (meters)
data_utm = data.to_crs("EPSG:32617")
print(f"UTM 17N CRS: {data_utm.crs}")
print(data_utm)
print()

# Transform to Web Mercator (web mapping)
data_merc = data.to_crs("EPSG:3857")
print(f"Web Mercator CRS: {data_merc.crs}")
print(data_merc)
print()

# Transform to State Plane Florida East (US feet)
data_sp = data.to_crs("EPSG:2236")
print(f"State Plane FL East CRS: {data_sp.crs}")
print(data_sp)
print()

# Distance calculations in different CRS
print("=== Distance calculations ===")
# In degrees (meaningless for distance)
dist_deg = data.geometry[0].distance(data.geometry[1])
print(f"Distance in degrees: {dist_deg:.6f} (meaningless)")

# In meters (UTM)
dist_m = data_utm.geometry[0].distance(data_utm.geometry[1])
print(f"Distance in meters (UTM): {dist_m:.2f} m")

# In US feet (State Plane)
dist_ft = data_sp.geometry[0].distance(data_sp.geometry[1])
print(f"Distance in US feet (State Plane): {dist_ft:.2f} ft")
print(f"  = {dist_ft * 0.3048:.2f} m")

# Area calculations
polygon = Polygon([(-80.93, 29.02), (-80.92, 29.02), (-80.92, 29.03), (-80.93, 29.03)])
poly_gdf = gpd.GeoDataFrame({"name": ["test"]}, geometry=[polygon], crs="EPSG:4326")
poly_utm = poly_gdf.to_crs("EPSG:32617")
area_deg = poly_gdf.geometry[0].area
area_m = poly_utm.geometry[0].area
print(f"\nArea in degrees^2: {area_deg:.10f} (meaningless)")
print(f"Area in m^2 (UTM): {area_m:.2f} m^2")
