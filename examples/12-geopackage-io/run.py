#!/usr/bin/env python3
"""Example 12: GeoPackage read/write with multiple layers."""
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Create multiple layers
points = gpd.GeoDataFrame(
    {"name": ["A", "B", "C"], "type": ["sensor", "camera", "beacon"]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01)],
    crs="EPSG:4326"
)

polygons = gpd.GeoDataFrame(
    {"zone": ["north", "south"], "area_km2": [12.5, 8.3]},
    geometry=[
        Polygon([(-80.95, 29.05), (-80.90, 29.05), (-80.90, 29.00), (-80.95, 29.00)]),
        Polygon([(-80.95, 29.00), (-80.90, 29.00), (-80.90, 28.95), (-80.95, 28.95)])
    ],
    crs="EPSG:4326"
)

# Write to GeoPackage (multiple layers)
gpkg_path = "output/data.gpkg"
points.to_file(gpkg_path, layer="points", driver="GPKG")
polygons.to_file(gpkg_path, layer="polygons", driver="GPKG")
print(f"Written to {gpkg_path}")

# Read layers
print("\n=== GeoPackage layers ===")
import sqlite3
conn = sqlite3.connect(gpkg_path)
cursor = conn.cursor()
cursor.execute("SELECT table_name FROM gpkg_contents")
tables = cursor.fetchall()
print(f"Layers: {[t[0] for t in tables]}")

# Read each layer
for table in tables:
    layer_name = table[0]
    gdf = gpd.read_file(gpkg_path, layer=layer_name)
    print(f"\nLayer '{layer_name}':")
    print(f"  Rows: {len(gdf)}")
    print(f"  Columns: {list(gdf.columns)}")
    print(f"  CRS: {gdf.crs}")

conn.close()

# Compare with Shapefile
print("\n=== GeoPackage vs Shapefile ===")
print("GeoPackage advantages:")
print("  - Single file (no .shp/.shx/.dbf/.prj)")
print("  - Multiple layers")
print("  - SQLite-based (queryable)")
print("  - Better type support")
print("  - No 2GB size limit")
