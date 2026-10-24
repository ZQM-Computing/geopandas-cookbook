# GeoPandas Patterns

<!-- ZQM-START -->
<!-- markdownlint-disable MD033 -->
<p align="center">
  <strong>ZQM Computing — Geospatial Engineering & Scientific Computing</strong><br>
  <a href="https://github.com/ZQM-Computing">ZQM Computing</a>
</p>
<!-- markdownlint-enable MD033 -->
<!-- ZQM-END -->

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![GitHub](https://img.shields.io/github/stars/ZQM-Computing/geopandas-cookbook?style=social)
[![CI](https://github.com/ZQM-Computing/geopandas-cookbook/actions/workflows/ci.yml/badge.svg)](https://github.com/ZQM-Computing/geopandas-cookbook/actions/workflows/ci.yml)

Production-tested GeoPandas/Shapely patterns for Python geospatial workflows — spatial joins, CRS handling, overlays, interpolation, and performance, all on synthetic data.

## Repository role and status

**Status:** Active, public.

**What this repository is:** GeoPandas/Shapely patterns for Python geospatial workflows — spatial joins, CRS handling, overlay, interpolation, and performance, all on synthetic data.

**What it contributes:** Part of the ZQM Computing public geospatial portfolio — production-grade pattern and reference repositories that document geospatial engineering practice across the stack. This repository is the reusable pattern library for its layer: working code and runbooks that practitioners can lift into their own pipelines, and portfolio evidence of the engineering practice behind ZQM Computing. The umbrella index for the series is [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks).

**Standing:** The portfolio program was completed and Tier-1 hardened on 2026-10-15, with prose CI enforced as required status checks. This repository is standalone — no other repository or deployment depends on it.

## Who this is for

Python developers, data scientists, and GIS analysts who work with vector geospatial data in Python. If your workflow is "load it, join it, reproject it, map it," these are the patterns that keep showing up.

## Prerequisites

- Python 3.11+
- `geopandas >= 0.14`, `shapely >= 2.0` (`pip install geopandas shapely`; add `fiona` for format I/O)

## Quickstart

```bash
pip install geopandas shapely

# Run any example directly — each is self-contained with synthetic data
python examples/01-spatial-joins/run.py
```

## Usage

Each pattern is a self-contained, runnable example. Start from the
[Quickstart](#quickstart), then open any entry in the [Patterns](#patterns)
list and run it end to end. Copy the pattern into your own project and
swap in your data — the patterns are reference implementations, not a
package to install.

## Patterns

| # | Example | What it demonstrates |
|---|---------|----------------------|
| 01 | `01-spatial-joins` | Point-in-polygon and nearest spatial joins |
| 02 | `02-crs-handling` | Reprojection and coordinate-system management (WGS84 → projected) |
| 03 | `03-geojson-io` | GeoJSON read/write with validation |
| 04 | `04-postgis-integration` | Reading from and writing to PostgreSQL/PostGIS |
| 05 | `05-plotting` | Static and interactive maps from GeoDataFrames |
| 06 | `06-performance` | Spatial indexing and vectorized operations on large synthetic data |
| 07 | `07-buffer-analysis` | Buffer-based proximity analysis (facilities vs. population points) |
| 08 | `08-overlay-operations` | Intersection, union, difference, symmetric difference |
| 09 | `09-spatial-interpolation` | IDW and nearest-neighbor interpolation from sample stations |
| 10 | `10-nearest-neighbor` | Nearest-facility analysis and facility coverage |
| 11 | `11-crs-transformation` | Multi-CRS transformation pipeline |
| 12 | `12-geopackage-io` | Multi-layer GeoPackage read/write |

## Repository layout

```text
geopandas-cookbook/
├── examples/
│   ├── 01-spatial-joins/run.py
│   └── ... (one run.py per pattern, 12 total)
├── tests/
│   └── test_patterns.py     # syntax checks for every example
├── pyproject.toml
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## Validation

```bash
pip install pytest
pytest            # verifies every example has valid Python syntax
```

CI runs `ruff check` / `ruff format --check` and the pytest suite on every push and pull request.

## Roadmap

- Parquet/GeoParquet round-trips with `pyarrow`
- Spatial join benchmarking: `sindex` vs. brute force at scale
- Dask-GeoPandas sketch for out-of-core workflows

## Contributing

See [CONTRIBUTING.md](https://github.com/ZQM-Computing/geopandas-cookbook/blob/main/CONTRIBUTING.md). Report security issues to <zqmcomputing@gmail.com> — please do not open a public issue for those.

## More from this series

- [postgis-cookbook](https://github.com/ZQM-Computing/postgis-cookbook) — Production PostGIS patterns: spatial indexing, joins & KNN, SRID management, vector tiles, data quality, partitioning
- [duckdb-spatial-cookbook](https://github.com/ZQM-Computing/duckdb-spatial-cookbook) — DuckDB Spatial patterns for analytical geospatial SQL: GeoParquet, spatial joins, KNN, H3 aggregation — no server required
- [pgrouting-cookbook](https://github.com/ZQM-Computing/pgrouting-cookbook) — pgRouting network analysis on PostGIS: shortest path, driving distance, isochrones, turn restrictions, traffic-aware routing
- [gdal-cookbook](https://github.com/ZQM-Computing/gdal-cookbook) — GDAL/OGR command-line patterns: conversion, reprojection, clipping, mosaicking — production-tested, runnable examples
- [stac-cookbook](https://github.com/ZQM-Computing/stac-cookbook) — STAC patterns for geospatial data discovery: catalogs, item validation, search API, bulk operations, cloud deployment
- [maplibre-cookbook](https://github.com/ZQM-Computing/maplibre-cookbook) — MapLibre GL JS patterns for frontend vector tile rendering: custom layers, 3D terrain, performance tuning, interactive maps
- [cog-cookbook](https://github.com/ZQM-Computing/cog-cookbook) — Cloud Optimized GeoTIFF patterns: creation, validation, TiTiler serving, xarray integration, performance benchmarking
- [geoparquet-cookbook](https://github.com/ZQM-Computing/geoparquet-cookbook) — GeoParquet patterns for columnar geospatial analytics: partitioning, predicate pushdown, DuckDB/Spark integration
- [h3-cookbook](https://github.com/ZQM-Computing/h3-cookbook) — H3 hexagonal grid patterns: indexing, aggregation, visualization, grid comparisons, performance benchmarks
- [qgis-resources](https://github.com/ZQM-Computing/qgis-resources) — QGIS expressions, PyQGIS snippets, Processing scripts, styles, and QField field-collection guides
- [geospatial-api-reference](https://github.com/ZQM-Computing/geospatial-api-reference) — OGC API – Features reference implementation with FastAPI and PostGIS backends
- [ollama-fleet-patterns](https://github.com/ZQM-Computing/ollama-fleet-patterns) — Ollama fleet operations: model management, health checks, load-spreading, VRAM budgeting, dependency-light RAG
- [proxmox-ceph-operations](https://github.com/ZQM-Computing/proxmox-ceph-operations) — Proxmox VE + Ceph operations runbooks: health checks, backup discipline, OSD replacement, upgrade checklists
- [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks) — Umbrella index for all ZQM geospatial pattern repos

## Documentation and validation

For setup instructions, reproducible examples, data provenance, CRS/SRID assumptions, security guidance, and dependency labels, follow the [ZQM geospatial repository documentation standard](https://github.com/ZQM-Computing/geospatial-cookbooks/blob/main/docs/repository-documentation-standard.md).

The configured CI workflow is the source of truth for automated checks. A passing workflow establishes only that its checks passed for that commit; it does not certify production deployment or prove that every dependency and operating environment was covered.

## License

MIT — see LICENSE file.

*Part of [ZQM Computing](https://github.com/ZQM-Computing) — geospatial engineering, scientific computing, and infrastructure patterns; the geospatial arm of [ZQM Labs](https://zqmlabs.com), makers of Z's Quests & Mischief location games.*
