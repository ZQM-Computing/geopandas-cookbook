"""Optional PostGIS round-trip; set GEOPANDAS_POSTGIS_URL to enable it."""
import os
import sys

database_url = os.environ.get("GEOPANDAS_POSTGIS_URL")
if not database_url:
    print("SKIP: set GEOPANDAS_POSTGIS_URL to run the PostGIS integration example.")
    raise SystemExit(0)

try:
    import geopandas as gpd
    import psycopg
except ImportError as exc:
    raise SystemExit("Install the optional dependency with: pip install 'psycopg[binary]'") from exc

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cur:
        cur.execute("CREATE TEMP TABLE cookbook_assets (asset_id integer, name text, geom geometry(Point, 4326))")
        cur.execute(
            "INSERT INTO cookbook_assets VALUES "
            "(1, 'North', ST_SetSRID(ST_MakePoint(-81.1, 29.2), 4326)), "
            "(2, 'South', ST_SetSRID(ST_MakePoint(-81.0, 29.1), 4326))"
        )
    assets = gpd.read_postgis(
        "SELECT asset_id, name, geom FROM cookbook_assets ORDER BY asset_id",
        conn,
        geom_col="geom",
    )
    assert len(assets) == 2 and assets.crs.to_epsg() == 4326
    print("Read two synthetic features from a temporary PostGIS table:")
    print(assets[["asset_id", "name"]].to_string(index=False))
