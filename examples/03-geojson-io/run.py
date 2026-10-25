"""Round-trip a validated GeoDataFrame through GeoJSON."""
import tempfile
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

source = gpd.GeoDataFrame(
    {"asset_id": [1, 2], "name": ["North", "South"]},
    geometry=[Point(-81.1, 29.2), Point(-81.0, 29.1)],
    crs="EPSG:4326",
)
assert source["asset_id"].is_unique
assert source.geometry.notna().all() and source.geometry.is_valid.all()
with tempfile.TemporaryDirectory(prefix="geopandas-geojson-") as tmp:
    path = Path(tmp) / "assets.geojson"
    source.to_file(path, driver="GeoJSON", index=False)
    restored = gpd.read_file(path)
    assert len(restored) == len(source)
    assert restored.crs is not None and restored.crs.to_epsg() == 4326
    assert set(restored["name"]) == {"North", "South"}
    print(f"Wrote and validated {len(restored)} features: {path.name}")
    print(restored[["asset_id", "name"]].to_string(index=False))
