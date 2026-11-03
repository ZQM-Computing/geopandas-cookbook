# Preliminary environmental constraints screening with GeoPandas

**Status:** synthetic executable example and regression tests included; not a tested regulatory product. Runtime CI evidence must be checked on the exact PR head. Use synthetic fixtures when implementing examples. The [umbrella resource guide](https://github.com/ZQM-Computing/geospatial-cookbooks/blob/main/docs/environmental-planning-resources.md) is proposed in a separate draft PR; until merged, that link may not resolve.

## Run the synthetic example

```bash
pip install -e . pytest
python examples/12-environmental-screening/run.py
python -m pytest tests/test_environmental_screening.py tests/test_parcel_environmental_screening.py tests/test_environmental_source_quality.py -q
```

The example reports per-type mapped overlap or missing coverage for synthetic features only. It does not fetch authoritative datasets, write client deliverables, or produce a regulatory conclusion.

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

## Synthetic acceptance tests and future extensions

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

Relevant existing patterns: spatial joins, CRS handling, geometry validation, overlays, and the [workflow diagnostic](workflow-diagnostic.md). The new example exercises a subset of the specification; it does not yet implement the complete source register, reason-coded quarantine, exports, or reviewer map.

**Escalation:** confirm official local zoning and comprehensive-plan controls; seek qualified wetland, ecological, floodplain, survey, engineering, or environmental assessment review where needed.

## Parcel-level resolution and confidence

The parcel-detail example (`examples/12-environmental-screening/parcel_detail.py`) screens multiple assessor-style parcel polygons independently. Each parcel/type result includes total area (m²/acres), source-covered area, unscreened area, known mapped overlap (m²/acres), and percentage of parcel covered and overlapped. Overlapping constraint polygons are unioned to prevent double counting. Partial source coverage is explicitly flagged, even when an overlap is known.

**Resolution is not accuracy.** Parcel IDs and polygons from an assessor are for screening and taxation, not necessarily surveyed legal boundaries. A high-resolution basemap or a map at 1:1,000 cannot improve a coarse NWI, soils, flood, or land-cover layer. Record source scale, horizontal accuracy, vintage, positional uncertainty, and map effective date for every layer. Treat near-boundary hits as review flags; do not interpret millimetre-level computational coordinates as centimetre-level field accuracy.

For Florida applications, obtain current parcel polygons and official zoning/future-land-use maps from the relevant county or municipality. Check boundary conflicts, easements, recorded plats, and the governing comprehensive plan separately. Do not infer buildable acreage from parcel area minus GIS overlaps without regulatory buffers, easements, access, and professional review.

**Known limitations:** The current parcel example assumes planar metre CRS and valid polygon geometry. It does not resolve parcel ownership, topology slivers, cadastral positional accuracy, regulatory setbacks, source effective dates, raster cell resolution, or legal buildability. It also does not fetch live parcels or authoritative environmental layers. The test fixtures are synthetic.

## Source resolution and boundary review

The source-quality module (`examples/12-environmental-screening/source_quality.py`) validates a minimum provenance record: dataset identifier, URL, access timestamp, effective date (or explicit unknown), horizontal accuracy in metres (or unknown), native resolution in metres (or unknown), and boundary basis. Values must be supplied by source metadata; do not infer them from rendering scale or coordinate precision.

A separate `boundary_review_flags` function identifies constraint geometries within a user-defined **review distance** of parcel boundaries. The distance is a sensitivity flag, not a regulatory buffer, positional-accuracy correction, or claim that a constraint crosses the legal parcel boundary. Review distances must be justified in the project methodology and should reflect available accuracy evidence.

These functions do not yet integrate into a single client-report pipeline. Future work should propagate the source record and flags into each parcel result and validate local authoritative data before operational use.
