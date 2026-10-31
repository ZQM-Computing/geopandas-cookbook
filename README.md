# GeoPandas Cookbook

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

A **GeoPandas and Shapely cookbook for Python GIS and spatial data analysis**. Learn spatial joins, coordinate reference system (CRS) transformations, overlays, geometry validation, interpolation, and performance-aware vector workflows using synthetic datasets. It is designed for Python developers, GIS analysts, and data engineers; confirm geometry validity, CRS units, library versions, and dataset scale before applying a pattern to production data.

## Repository role and status

**Status:** Active, public.

**What this repository is:** GeoPandas/Shapely patterns for Python geospatial workflows — spatial joins, CRS handling, overlay, interpolation, and performance, all on synthetic data.

**What it contributes:** Part of the ZQM Computing geospatial portfolio. This repository provides examples and guidance for the tools and workflows described below; validate each example against your own data, software versions, and operating environment before adopting it. The umbrella index for the series is [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks).

**Standing:** This repository is maintained independently. Automated checks cover only the paths and environments configured in its workflows; they do not establish production readiness or operational certification.

## Who this is for

Python developers, data scientists, and GIS analysts who work with vector geospatial data in Python. If your workflow is "load it, join it, reproject it, map it," these are the patterns that keep showing up.

## Prerequisites

- Python 3.11+
- Core dependencies are declared in `pyproject.toml`; install with `pip install -e .`.
- Optional integrations: `pip install -e '.[postgis,interactive]'` for PostGIS connectivity and interactive Folium maps.

## Quickstart

```bash
pip install -e .

# Run any example directly — each uses synthetic data
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
pytest            # verifies all 12 examples exist, compile, and execute
```

CI runs syntax and example smoke tests on every push and pull request. Examples use synthetic data; the PostGIS example skips unless `GEOPANDAS_POSTGIS_URL` is set. Optional interactive maps require `pip install -e '.[interactive]'`.

## Scale benchmarking

The performance example defaults to 20,000 deterministic points for CI and compares three nested query windows (selective, moderate, broad). Choose `--distribution uniform`, `clustered`, or `mixed` to test sensitivity to spatial layout; the latter two use deterministic Gaussian clusters, and `mixed` combines 70% clustered with 30% uniform points. It reports match fraction, index-query median, vectorized-scan median, and exact feature-position equivalence for each window. Index-build time is reported separately. These synthetic layouts illustrate sensitivity, not real-world performance guarantees. Run larger local workloads explicitly:

```bash
python examples/06-performance/run.py --features 1000000 --repeats 3 --distribution uniform
python examples/06-performance/run.py --features 1000000 --repeats 3 --distribution clustered
python examples/06-performance/run.py --features 1000000 --repeats 3 --distribution mixed
python examples/06-performance/run.py --features 10000000 --repeats 3 --distribution clustered
python examples/06-performance/run.py --features 50000000 --repeats 1 --distribution clustered
```

The 10M and especially 50M runs require substantial RAM for the GeoSeries and spatial index. Run them on a suitably provisioned host, record the software versions and available memory, and do not treat a single synthetic run as a production performance claim.

## Roadmap

- Parquet/GeoParquet round-trips with `pyarrow`
- Dask-GeoPandas sketch for out-of-core workflows

## Contributing

See [CONTRIBUTING.md](https://github.com/ZQM-Computing/geopandas-cookbook/blob/main/CONTRIBUTING.md). Report security issues to <zqmcomputing@gmail.com> — please do not open a public issue for those.

## More from this series

- [postgis-cookbook](https://github.com/ZQM-Computing/postgis-cookbook) — PostGIS SQL examples: spatial indexing, joins & KNN, SRID management, vector tiles, data quality, partitioning
- [duckdb-spatial-cookbook](https://github.com/ZQM-Computing/duckdb-spatial-cookbook) — DuckDB Spatial patterns for analytical geospatial SQL: GeoParquet, spatial joins, KNN, H3 aggregation — no server required
- [pgrouting-cookbook](https://github.com/ZQM-Computing/pgrouting-cookbook) — pgRouting network analysis on PostGIS: shortest path, driving distance, isochrones, turn restrictions, traffic-aware routing
- [gdal-cookbook](https://github.com/ZQM-Computing/gdal-cookbook) — GDAL/OGR command-line examples for conversion, reprojection, clipping, and mosaicking
- [stac-cookbook](https://github.com/ZQM-Computing/stac-cookbook) — STAC patterns for geospatial data discovery: catalogs, item validation, search API, bulk operations, cloud deployment
- [maplibre-cookbook](https://github.com/ZQM-Computing/maplibre-cookbook) — MapLibre GL JS patterns for frontend vector tile rendering: custom layers, 3D terrain, performance tuning, interactive maps
- [cog-cookbook](https://github.com/ZQM-Computing/cog-cookbook) — Cloud Optimized GeoTIFF patterns: creation, validation, TiTiler serving, xarray integration, performance benchmarking
- [geoparquet-cookbook](https://github.com/ZQM-Computing/geoparquet-cookbook) — GeoParquet patterns for columnar geospatial analytics: partitioning, predicate pushdown, DuckDB/Spark integration
- [h3-cookbook](https://github.com/ZQM-Computing/h3-cookbook) — H3 hexagonal grid patterns: indexing, aggregation, visualization, grid comparisons, performance benchmarks
- [qgis-resources](https://github.com/ZQM-Computing/qgis-resources) — QGIS expressions, PyQGIS snippets, Processing scripts, styles, and QField field-collection guides
- [geospatial-api-reference](https://github.com/ZQM-Computing/geospatial-api-reference) — OGC API – Features reference implementation with FastAPI and PostGIS backends
- [ollama-fleet-cookbook](https://github.com/ZQM-Computing/ollama-fleet-cookbook) — Ollama fleet operations: model management, health checks, load-spreading, VRAM budgeting, dependency-light RAG
- [proxmox-ceph-operations](https://github.com/ZQM-Computing/proxmox-ceph-operations) — Proxmox VE + Ceph operations runbooks: health checks, backup discipline, OSD replacement, upgrade checklists
- [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks) — Umbrella index for ZQM Computing geospatial cookbooks

## Documentation and validation

For setup instructions, reproducible examples, data provenance, CRS/SRID assumptions, security guidance, and dependency labels, follow the [ZQM geospatial repository documentation standard](https://github.com/ZQM-Computing/geospatial-cookbooks/blob/main/docs/repository-documentation-standard.md).

The configured CI workflow is the source of truth for automated checks. A passing workflow establishes only that its checks passed for that commit; it does not certify production deployment or prove that every dependency and operating environment was covered.

## License

MIT — see LICENSE file.

*Part of [ZQM Computing](https://github.com/ZQM-Computing) — geospatial engineering, scientific computing, and infrastructure patterns; the geospatial arm of [ZQM Labs](https://zqmlabs.com), makers of Z's Quests & Mischief location games.*
