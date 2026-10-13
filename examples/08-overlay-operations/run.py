#!/usr/bin/env python3
"""Example 08: Overlay operations (intersection, union, difference, symmetric difference)."""
import geopandas as gpd
from shapely.geometry import Polygon

# Create synthetic zones
zones = gpd.GeoDataFrame(
    {"zone": ["residential", "commercial", "industrial"], "tax_rate": [0.02, 0.03, 0.04]},
    geometry=[
        Polygon([(-80.95, 29.05), (-80.92, 29.05), (-80.92, 29.02), (-80.95, 29.02)]),
        Polygon([(-80.92, 29.05), (-80.90, 29.05), (-80.90, 29.00), (-80.92, 29.00)]),
        Polygon([(-80.90, 29.05), (-80.88, 29.05), (-80.88, 28.95), (-80.90, 28.95)])
    ],
    crs="EPSG:4326"
)

# Create synthetic parcels
parcels = gpd.GeoDataFrame(
    {"parcel_id": ["P001", "P002", "P003", "P004"], "value": [250000, 180000, 320000, 150000]},
    geometry=[
        Polygon([(-80.94, 29.04), (-80.93, 29.04), (-80.93, 29.03), (-80.94, 29.03)]),
        Polygon([(-80.93, 29.04), (-80.92, 29.04), (-80.92, 29.03), (-80.93, 29.03)]),
        Polygon([(-80.91, 29.04), (-80.90, 29.04), (-80.90, 29.01), (-80.91, 29.01)]),
        Polygon([(-80.90, 29.02), (-80.89, 29.02), (-80.89, 29.00), (-80.90, 29.00)])
    ],
    crs="EPSG:4326"
)

# Spatial join: which zone is each parcel in?
parcels_with_zone = gpd.sjoin(parcels, zones, how="left", predicate="within")
print("=== Parcel-zone assignment ===")
print(parcels_with_zone[["parcel_id", "zone", "tax_rate", "value"]])

# Calculate tax revenue by zone
tax = parcels_with_zone.groupby("zone").agg(
    parcel_count=("parcel_id", "count"),
    total_value=("value", "sum"),
    estimated_tax=("value", lambda x: (x * parcels_with_zone.loc[x.index, "tax_rate"]).sum())
)
print("\n=== Tax revenue by zone ===")
print(tax)

# Intersection: parcels that span multiple zones
print("\n=== Parcel area by zone ===")
for idx, parcel in parcels.iterrows():
    for _, zone in zones.iterrows():
        if parcel.geometry.intersects(zone.geometry):
            intersection_area = parcel.geometry.intersection(zone.geometry).area
            pct = intersection_area / parcel.geometry.area * 100
            if pct > 5:
                print(f"  {parcel['parcel_id']} in {zone['zone']}: {pct:.1f}%")
