"""Write and read multiple vector layers in one GeoPackage."""
import tempfile
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point, box

with tempfile.TemporaryDirectory(prefix="geopandas-gpkg-") as tmp:
    path = Path(tmp) / "field_assets.gpkg"
    sites = gpd.GeoDataFrame(
        {"site_id": [1, 2], "name": ["North", "South"]},
        geometry=[Point(-81.1, 29.3), Point(-81.0, 29.1)],
        crs="EPSG:4326",
    )
    zones = gpd.GeoDataFrame(
        {"zone_id": [10]}, geometry=[box(-81.2, 29.0, -80.9, 29.4)], crs="EPSG:4326"
    )
    sites.to_file(path, layer="sites", driver="GPKG", index=False)
    zones.to_file(path, layer="zones", driver="GPKG", index=False)
    restored_sites = gpd.read_file(path, layer="sites")
    restored_zones = gpd.read_file(path, layer="zones")
    assert len(restored_sites) == 2 and len(restored_zones) == 1
    assert restored_sites.crs is not None and restored_sites.crs.to_epsg() == 4326
    assert restored_zones.crs is not None and restored_zones.crs.to_epsg() == 4326
    assert restored_sites["site_id"].tolist() == [1, 2]
    assert restored_sites["name"].tolist() == ["North", "South"]
    assert restored_zones["zone_id"].tolist() == [10]
    assert restored_sites.geometry.iloc[0].equals(sites.geometry.iloc[0])
    assert restored_zones.geometry.iloc[0].equals(zones.geometry.iloc[0])
    print(f"GeoPackage contains {len(restored_sites)} sites and {len(restored_zones)} zone(s)")
