"""Example 09: Spatial interpolation (IDW, nearest neighbor)."""

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

# Create sample weather stations with temperature readings
np.random.seed(42)
stations = gpd.GeoDataFrame(
    {"station": ["S1", "S2", "S3", "S4", "S5"], "temp": [72.0, 68.5, 75.2, 70.1, 66.8]},
    geometry=gpd.points_from_xy(np.random.uniform(-80.94, -80.89, 5), np.random.uniform(28.99, 29.04, 5)),
    crs="EPSG:4326",
)

# Create grid of points to interpolate
grid_lons = np.linspace(-80.94, -80.89, 10)
grid_lats = np.linspace(28.99, 29.04, 10)
grid_points = []
for lon in grid_lons:
    for lat in grid_lats:
        grid_points.append(Point(lon, lat))

grid = gpd.GeoDataFrame({"id": range(len(grid_points))}, geometry=grid_points, crs="EPSG:4326")


# IDW interpolation (pure numpy, no scipy dependency)
def idw_interpolate(stations, grid_points, power=2):
    """Inverse Distance Weighting interpolation."""
    station_coords = np.array([(geom.x, geom.y) for geom in stations.geometry])
    station_values = stations["temp"].values

    interpolated = []

    for point in grid_points:
        dists = np.sqrt(np.sum((station_coords - [point.x, point.y]) ** 2, axis=1))
        # Avoid division by zero
        dists = np.maximum(dists, 1e-10)
        weights = 1.0 / np.power(dists, power)
        weights = weights / weights.sum()
        interpolated.append(np.sum(weights * station_values))

    return np.array(interpolated)


temps = idw_interpolate(stations, grid_points)
grid["temp"] = temps

print("=== IDW Interpolation Results ===")
print(f"Stations: {len(stations)}")
print(f"Grid points: {len(grid)}")
print(f"Min temp: {temps.min():.1f}F")
print(f"Max temp: {temps.max():.1f}F")
print(f"Mean temp: {temps.mean():.1f}F")

# Find hotspots (above 72F)
hotspots = grid[grid["temp"] > 72]
print(f"\nHotspots (>72F): {len(hotspots)}")
