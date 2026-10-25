"""Reproject geographic coordinates before measuring distances or areas."""
import geopandas as gpd
from shapely.geometry import Point, Polygon

sites = gpd.GeoDataFrame(
    {"site": ["A", "B"]},
    geometry=[Point(-81.1, 29.2), Point(-81.0, 29.2)],
    crs="EPSG:4326",
)
geographic_distance = sites.geometry.iloc[0].distance(sites.geometry.iloc[1])
metric = sites.to_crs("EPSG:32617")
metric_distance = metric.geometry.iloc[0].distance(metric.geometry.iloc[1])
area = gpd.GeoSeries(
    [Polygon([(-81.12, 29.18), (-81.08, 29.18), (-81.08, 29.22), (-81.12, 29.22)])],
    crs="EPSG:4326",
).to_crs("EPSG:32617").area.iloc[0]
print(f"Raw degree distance (not metres): {geographic_distance:.6f}")
print(f"UTM distance: {metric_distance:.1f} m")
print(f"Projected polygon area: {area:.0f} m²")
assert metric_distance > 9_000 and metric_distance < 11_000
