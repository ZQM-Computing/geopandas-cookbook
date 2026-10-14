"""Example 05: Plotting with GeoPandas."""

import geopandas as gpd
import matplotlib
from shapely.geometry import Point, Polygon

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Create synthetic data
points = gpd.GeoDataFrame(
    {"name": ["A", "B", "C"], "value": [10, 20, 30]},
    geometry=[Point(-80.93, 29.02), Point(-80.92, 29.03), Point(-80.91, 29.01)],
    crs="EPSG:4326",
)

polygons = gpd.GeoDataFrame(
    {"zone": ["north", "south"]},
    geometry=[
        Polygon([(-80.95, 29.05), (-80.90, 29.05), (-80.90, 29.00), (-80.95, 29.00)]),
        Polygon([(-80.95, 29.00), (-80.90, 29.00), (-80.90, 28.95), (-80.95, 28.95)]),
    ],
    crs="EPSG:4326",
)

# Plot points
fig, ax = plt.subplots(figsize=(8, 6))
polygons.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.5)
points.plot(ax=ax, color="red", markersize=100)
for idx, row in points.iterrows():
    ax.annotate(row["name"], (row.geometry.x, row.geometry.y))
plt.title("Synthetic Points and Polygons")
plt.savefig("output.png", dpi=150)
print("Saved to output.png")

# Choropleth plot
polygons["count"] = [3, 2]
fig, ax = plt.subplots(figsize=(8, 6))
polygons.plot(ax=ax, column="count", cmap="YlOrRd", edgecolor="black", legend=True)
plt.title("Choropleth by Count")
plt.savefig("choropleth.png", dpi=150)
print("Saved to choropleth.png")
