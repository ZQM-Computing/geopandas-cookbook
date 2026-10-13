#!/usr/bin/env python3
"""Example 03: GeoJSON read/write with validation."""
import geopandas as gpd
from shapely.geometry import Point
import json

# Create synthetic data
points = gpd.GeoDataFrame(
    {"name": ["A", "B", "C"], "value": [10, 20, 30]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01)],
    crs="EPSG:4326"
)

# Write to GeoJSON
points.to_file("output.geojson", driver="GeoJSON")
print("Written to output.geojson")

# Read back
loaded = gpd.read_file("output.geojson")
print("Read back:")
print(loaded)
print()

# Validate: check CRS and geometry type
print("CRS:", loaded.crs)
print("Geometry types:", loaded.geom_type.unique())
print("Valid geometries:", loaded.is_valid.all())
