"""Example 04: PostGIS integration with GeoPandas."""

import geopandas as gpd
from shapely.geometry import Point

# Create synthetic data
points = gpd.GeoDataFrame(
    {"name": ["A", "B", "C"], "value": [10, 20, 30]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01)],
    crs="EPSG:4326",
)

# Write to PostGIS (requires running PostgreSQL with PostGIS)
# engine = create_engine("postgresql://user:pass@localhost:5432/gis")
# points.to_postgis("points", engine, if_exists="replace")

# Read from PostGIS
# loaded = gpd.read_postgis("SELECT * FROM points", engine)

# For demo: write to GeoJSON and read back
points.to_file("output.geojson", driver="GeoJSON")
loaded = gpd.read_file("output.geojson")
print("PostGIS round-trip (simulated with GeoJSON):")
print(loaded)
print()

# SQL query example
# query = "SELECT * FROM points WHERE value > 15"
# result = gpd.read_postgis(query, engine)
