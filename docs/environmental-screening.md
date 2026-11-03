# Preliminary environmental constraints screening with GeoPandas

**Status:** documented workflow specification, not a tested regulatory product. Use synthetic fixtures when implementing examples. The [umbrella resource guide](https://github.com/ZQM-Computing/geospatial-cookbooks/blob/main/docs/environmental-planning-resources.md) is proposed in a separate draft PR; until merged, that link may not resolve.

## Question

For a candidate development footprint, which mapped environmental constraints overlap the footprint, and how much of each overlap is supported by the available source data?

This is desktop screening only, not a wetland delineation, certified survey, flood determination, permit opinion, or substitute for local professional review.

## Inputs and data contract

- Candidate polygons: stable `site_id`, valid geometry, declared CRS and boundary provenance.
- Constraint layers: stable `feature_id`, `constraint_type`, authoritative source identifier, effective/published date, and CRS.
- Source register: URL, access timestamp, license, coverage extent, positional accuracy, scale/resolution, and known exclusions.
- Optional analysis buffer: explicitly documented distance and projected CRS units; **not** a regulatory setback unless verified against the applicable rule.

Never assume that a missing record means there is no constraint.

## Processing sequence

1. Load immutable originals and record file hashes, source dates, counts, and CRS.
2. Validate nonempty geometry and unique IDs; quarantine null, invalid, duplicate, or mixed-CRS records with reason codes. Do not silently repair authoritative boundaries.
3. Transform all layers to an appropriate local projected CRS for area/distance. Verify axis order and units; do not compute acreage from longitude/latitude degrees.
4. Distinguish **coverage absent** from **no mapped intersection** using the source's coverage footprint.
5. For each site and constraint type, intersect polygons with `geopandas.overlay(..., how="intersection")`. Dissolve overlapping features *within the same constraint type* before summing, or double counting will inflate area.
6. Calculate `overlap_m2`, `overlap_acres = overlap_m2 / 4046.8564224`, and `pct_site = 100 * overlap_m2 / site_area_m2`. Preserve raw geometry and numeric precision; round only presentation values.
7. Record source feature IDs and method version. Emit `intersects`, `no_mapped_intersection`, `no_source_coverage`, or `processing_error` separately.
8. Reconcile all site IDs, source counts, overlap areas, and failures. Export GeoPackage/GeoParquet and a CSV constraint matrix; review maps and assumptions manually.

## Acceptance tests for a future executable pattern

| Fixture | Expected result |
| --- | --- |
| Synthetic 100 m × 100 m site with 50 m × 100 m constraint | 5,000 m² overlap, 50% |
| Two identical constraint polygons of the same type | 5,000 m² after union, not 10,000 m² |
| Constraint polygon outside the site, within source coverage | `no_mapped_intersection` |
| Site outside documented source coverage | `no_source_coverage`, not zero-risk |
| Geographic CRS used directly for area | Reproject or fail explicitly; never report degree² as m² |
| Invalid geometry, duplicate site ID, missing CRS | Quarantine with a reason; no silently successful result |
| One failed layer while others succeed | Preserve per-layer error and mark screening incomplete |
| Repeated run on identical synthetic inputs | Identical IDs, counts, area values, and source-register metadata |

## Planning deliverables

A reviewer should receive a constraint matrix, map per alternative, source/provenance register, rejected-feature report, uncertainty notes, and specialist follow-up list. Avoid ranking parcels using a single unqualified suitability score. Keep zoning, future land use, FEMA flood hazard, NWI wetlands, NRCS soils, protected species, and EPA/state water-quality evidence in separate categories.

Relevant existing patterns: spatial joins, CRS handling, geometry validation, overlays, and the [workflow diagnostic](workflow-diagnostic.md). These patterns do not themselves validate the environmental screening described here.

**Escalation:** confirm official local zoning and comprehensive-plan controls; seek qualified wetland, ecological, floodplain, survey, engineering, or environmental assessment review where needed.
