# EXAMPLES-TODO — geopandas-cookbook

> **Status: GAP, NOT DONE.** This file is a tracker, not a substitute for
> examples. The 12 examples below are promised by README.md, docs/index.md,
> and the repository layout tree, but `examples/` does **not exist** in this
> repo as of the 2026-10-24 investigation. The quickstart command
> `python examples/01-spatial-joins/run.py` currently fails, and the
> "Production-tested" claim in README/docs is currently false for that
> reason. Do not delete this file until every item below exists and the
> test suite passes with examples present.
>
> `tests/test_patterns.py::test_examples_present` intentionally fails
> while this gap is open. It asserts only that `examples/` exists and is
> non-empty; tighten it to exactly 12 files once all 12 below land.

## Promised examples (all MISSING)

| # | Directory | Entry point | What README/docs say it demonstrates |
|---|-----------|-------------|---------------------------------------|
| 01 | `01-spatial-joins` | `run.py` | Point-in-polygon and nearest spatial joins |
| 02 | `02-crs-handling` | `run.py` | Reprojection and coordinate-system management (WGS84 → projected) |
| 03 | `03-geojson-io` | `run.py` | GeoJSON read/write with validation |
| 04 | `04-postgis-integration` | `run.py` | Reading from and writing to PostgreSQL/PostGIS |
| 05 | `05-plotting` | `run.py` | Static and interactive maps from GeoDataFrames |
| 06 | `06-performance` | `run.py` | Spatial indexing and vectorized operations on large synthetic data |
| 07 | `07-buffer-analysis` | `run.py` | Buffer-based proximity analysis (facilities vs. population points) |
| 08 | `08-overlay-operations` | `run.py` | Intersection, union, difference, symmetric difference |
| 09 | `09-spatial-interpolation` | `run.py` | IDW and nearest-neighbor interpolation from sample stations |
| 10 | `10-nearest-neighbor` | `run.py` | Nearest-facility analysis and facility coverage |
| 11 | `11-crs-transformation` | `run.py` | Multi-CRS transformation pipeline |
| 12 | `12-geopackage-io` | `run.py` | Multi-layer GeoPackage read/write |

## Suggested order

1. `01-spatial-joins/run.py` first — it is the README quickstart example,
   so landing it alone makes the first command a visitor tries actually run.
2. The remaining 11, in table order.
3. Then declare the real dependencies (`geopandas >= 0.14`,
   `shapely >= 2.0`, `fiona` for format I/O) in `pyproject.toml` or add a
   `requirements.txt` — they currently live only in README prose.
4. Then tighten `test_examples_present` to assert exactly 12 `*/run.py`
   files, and delete this file.
