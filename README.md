# GeoPandas Patterns

Production-tested GeoPandas/Shapely patterns for Python geospatial workflows.

## Who this is for

Python developers, data scientists, and GIS analysts who work with geospatial data.

## What's inside

- `examples/` — Runnable scripts with sample data
- `tests/` — Validation tests for each pattern

## Patterns

| # | Pattern | Description |
|---|---------|-------------|
| 1 | Spatial joins | Point-in-polygon, intersection, nearest |
| 2 | CRS handling | Reprojection and coordinate system management |
| 3 | GeoJSON I/O | Read/write GeoJSON with validation |
| 4 | PostGIS integration | Read/write from PostgreSQL/PostGIS |
| 5 | Plotting | Static and interactive maps |
| 6 | Performance | Spatial indexing and vectorized operations |
| 7 | Buffer analysis | Proximity and service area analysis |
| 8 | Overlay operations | Intersection, union, difference, symmetric difference |
| 9 | Spatial interpolation | IDW interpolation |
| 10 | Nearest neighbor | Facility coverage and nearest facility |
| 11 | CRS transformation | Multi-CRS transformation pipeline |
| 12 | GeoPackage I/O | Multi-layer GeoPackage read/write |

## Requirements

- Python 3.11+
- GeoPandas >= 0.14
- Shapely >= 2.0
- Fiona >= 1.9

## Quick start

```bash
pip install -e .
pytest
```

## License

MIT — see LICENSE file.

## Related repositories

- [ZQM Geospatial Patterns](https://github.com/ZQM-Computing/geospatial-patterns) — umbrella index of all geospatial pattern repos
- [postgis-patterns](https://github.com/ZQM-Computing/postgis-patterns) — production PostGIS patterns & best practices
- [duckdb-spatial-patterns](https://github.com/ZQM-Computing/duckdb-spatial-patterns) — DuckDB Spatial patterns for analytical geospatial SQL
- [geospatial-api-reference](https://github.com/ZQM-Computing/geospatial-api-reference) — OGC API - Features with FastAPI + PostGIS
- [qgis-resources](https://github.com/ZQM-Computing/qgis-resources) — QGIS expressions, PyQGIS, styles, and QField guides
- [proxmox-ceph-operations](https://github.com/ZQM-Computing/proxmox-ceph-operations) — Proxmox VE + Ceph operations runbooks
- [ollama-fleet-patterns](https://github.com/ZQM-Computing/ollama-fleet-patterns) — Ollama fleet operations & a minimal RAG reference

*Part of [ZQM Labs](https://github.com/ZQM-Computing) — games, gear & a little mischief.*

