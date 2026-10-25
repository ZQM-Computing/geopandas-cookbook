"""Optional PostGIS round-trip; set GEOPANDAS_POSTGIS_URL to enable it."""
import os

database_url = os.environ.get("GEOPANDAS_POSTGIS_URL")
if not database_url:
    print("SKIP: set GEOPANDAS_POSTGIS_URL to run the PostGIS integration example.")
    raise SystemExit(0)

try:
    from sqlalchemy import create_engine, text
    import geopandas as gpd
except ImportError as exc:
    raise SystemExit("Install the optional dependency with: pip install -e '.[postgis]'") from exc

# psycopg 3 URLs are explicit so the optional extra controls the driver.
if database_url.startswith("postgres://"):
    database_url = "postgresql+psycopg://" + database_url.removeprefix("postgres://")
elif database_url.startswith("postgresql://"):
    database_url = "postgresql+psycopg://" + database_url.removeprefix("postgresql://")

engine = create_engine(database_url)
try:
    # The table is temporary and exists only on this connection. No persistent
    # schema object is created or replaced in the caller's database.
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TEMP TABLE cookbook_assets "
            "(asset_id integer PRIMARY KEY, name text, geom geometry(Point, 4326))"
        ))
        conn.execute(
            text(
                "INSERT INTO cookbook_assets (asset_id, name, geom) VALUES "
                "(:asset_id, :name, ST_SetSRID(ST_MakePoint(:x, :y), 4326))"
            ),
            [
                {"asset_id": 1, "name": "North", "x": -81.1, "y": 29.2},
                {"asset_id": 2, "name": "South", "x": -81.0, "y": 29.1},
            ],
        )
        assets = gpd.read_postgis(
            "SELECT asset_id, name, geom FROM cookbook_assets ORDER BY asset_id",
            conn,
            geom_col="geom",
        )
        assert len(assets) == 2 and assets.crs.to_epsg() == 4326
        print("Read two synthetic features from a temporary PostGIS table:")
        print(assets[["asset_id", "name"]].to_string(index=False))
finally:
    engine.dispose()
