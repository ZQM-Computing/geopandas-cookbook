#!/usr/bin/env python3
"""Example 02: CRS handling and reprojection."""
import geopandas as gpd
from shapely.geometry import Point

# Create points in WGS84
points = gpd.GeoDataFrame(
    {"name": ["A", "B", "C"]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01)],
    crs="EPSG:4326"
)
print("Original CRS:", points.crs)
print(points)
print()

# Reproject to UTM Zone 17N
points_utm = points.to_crs("EPSG:32617")
print("Reprojected to UTM 17N:")
print(points_utm)
print()

# Reproject to Web Mercator
points_merc = points.to_crs("EPSG:3857")
print("Reprojected to Web Mercator:")
print(points_merc)
