"""Measure facility proximity in a projected CRS using buffers."""
import geopandas as gpd
from shapely.geometry import Point

facilities = gpd.GeoDataFrame(
    {"facility": ["A", "B"]},
    geometry=[Point(-81.1, 29.2), Point(-80.95, 29.2)],
    crs="EPSG:4326",
).to_crs("EPSG:32617")
population = gpd.GeoDataFrame(
    {"population_id": range(1, 7)},
    geometry=[Point(-81.11, 29.2), Point(-81.10, 29.205), Point(-81.02, 29.2),
              Point(-80.95, 29.21), Point(-80.90, 29.2), Point(-81.3, 29.2)],
    crs="EPSG:4326",
).to_crs("EPSG:32617")
buffers = facilities[["facility", "geometry"]].copy()
buffers["geometry"] = buffers.geometry.buffer(1_000)
covered = gpd.sjoin(population, buffers, how="left", predicate="within")
counts = covered.groupby("facility")["population_id"].nunique()
print("Population points within 1 km of each facility:")
print(counts.to_string())
print(f"Covered unique population points: {covered.loc[covered.facility.notna(), 'population_id'].nunique()}")
