# Preliminary environmental constraints screening with GeoPandas

**Status:** synthetic executable example and regression tests included; not a tested regulatory product. Runtime CI evidence must be checked on the exact PR head. Use synthetic fixtures when implementing examples. The [proposed umbrella resource guide](https://github.com/ZQM-Computing/geospatial-cookbooks/pull/36) remains a separate draft; review its source references before adopting it.

## Run the synthetic example

```bash
pip install -e . pytest
python examples/12-environmental-screening/run.py
python -m pytest -q
```

The example reports per-type mapped overlap or missing coverage for synthetic features only. It does not fetch authoritative datasets, write client deliverables, or produce a regulatory conclusion.

## Build the complete synthetic parcel bundle

```bash
python examples/12-environmental-screening/demo_bundle.py /tmp/zqm-parcel-demo
```

On Windows, choose a writable new directory such as `C:/Temp/zqm-parcel-demo`.
The command uses two synthetic parcels and two constraint types. It creates
five files: `parcel_constraints.csv`, `parcel_screening.json`,
`parcel_screening.gpkg`, `parcel_review_map.png`, and `manifest.json`, then
verifies their inventory and checksums. An existing destination is refused.
All source URLs, access timestamps and geometry in this command are labeled
fixtures; no source is downloaded or independently authenticated.

Expected findings: DEMO-P1 has 5,000 m² of unioned wetland overlap despite a
duplicate input feature. DEMO-P2 has 50% flood-source coverage with 2,500 m²
of known mapped overlap, while its wetland coverage is absent. Neither
partial nor absent coverage is a complete negative result.

Analytical results are repeatable for the fixture and software versions.
GeoPackage creation metadata can change file bytes between runs; each
manifest verifies its own completed bundle rather than promising identical
binary hashes across independent runs.

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

Relevant existing patterns: spatial joins, CRS handling, geometry validation, overlays, and the [workflow diagnostic](workflow-diagnostic.md). The current modules provide the parcel matrix, minimum source register, CSV/JSON reports, GeoPackage, reviewer map and manifest. Full source licensing/feature-level lineage, reason-coded quarantine, per-layer error recovery and representative authoritative-data validation remain future work.

**Escalation:** confirm official local zoning and comprehensive-plan controls; seek qualified wetland, ecological, floodplain, survey, engineering, or environmental assessment review where needed.

## Parcel-level resolution and confidence

The parcel-detail example (`examples/12-environmental-screening/parcel_detail.py`) screens multiple assessor-style parcel polygons independently. Each parcel/type result includes total area (m²/acres), source-covered area, unscreened area, known mapped overlap (m²/acres), and percentage of parcel covered and overlapped. Overlapping constraint polygons are unioned to prevent double counting. Partial source coverage is explicitly flagged, even when an overlap is known.

**Resolution is not accuracy.** Parcel IDs and polygons from an assessor are for screening and taxation, not necessarily surveyed legal boundaries. A high-resolution basemap or a map at 1:1,000 cannot improve a coarse NWI, soils, flood, or land-cover layer. Record source scale, horizontal accuracy, vintage, positional uncertainty, and map effective date for every layer. Treat near-boundary hits as review flags; do not interpret millimetre-level computational coordinates as centimetre-level field accuracy.

For Florida applications, obtain current parcel polygons and official zoning/future-land-use maps from the relevant county or municipality. Check boundary conflicts, easements, recorded plats, and the governing comprehensive plan separately. Do not infer buildable acreage from parcel area minus GIS overlaps without regulatory buffers, easements, access, and professional review.

**Known limitations:** The current parcel example assumes planar metre CRS and valid polygon geometry. It does not resolve parcel ownership, topology slivers, cadastral positional accuracy, regulatory setbacks, source effective dates, raster cell resolution, or legal buildability. It also does not fetch live parcels or authoritative environmental layers. The test fixtures are synthetic.

## Source resolution and boundary review

The source-quality module (`examples/12-environmental-screening/source_quality.py`) validates a minimum provenance record: dataset identifier, URL, access timestamp, effective date (or explicit unknown), horizontal accuracy in metres (or unknown), native resolution in metres (or unknown), and boundary basis. Values must be supplied by source metadata; do not infer them from rendering scale or coordinate precision.

A separate `boundary_review_flags` function identifies constraint geometries within a user-defined **review distance** of parcel boundaries. The distance is a sensitivity flag, not a regulatory buffer, positional-accuracy correction, or claim that a constraint crosses the legal parcel boundary. Review distances must be justified in the project methodology and should reflect available accuracy evidence.

The bundle validates and includes the minimum source records in its JSON report. Boundary-review flags are still a separate helper; they are not propagated into each parcel result. Integration with current authoritative data and project-specific source licensing remains unvalidated.

## Deterministic parcel screening reports

The reporting module (`examples/12-environmental-screening/reporting.py`) accepts parcel-level screening rows and emits `parcel_constraints.csv` and `parcel_screening.json`. It sorts by parcel ID and constraint type, rejects duplicate keys, checks finite nonnegative measurements, and verifies coverage and overlap arithmetic before writing. JSON includes a clearly labeled preliminary-screening disclaimer and an optional source-register payload. The module does not fetch live parcel data or infer source accuracy. Store reports according to the project's confidentiality and retention requirements; generated outputs should not be committed with client parcel data.

The report writer now validates supplied source-register records, requires one source record per reported constraint type, and checks that parcel status, overlap, acreage, and coverage measurements agree. Missing source metadata is explicitly marked as not provided rather than implying verified provenance. The writer still does not perform atomic multi-file replacement; client workflows should publish completed bundles only after all checks succeed.

## Spatial GeoPackage deliverable

The GeoPackage export module (`examples/12-environmental-screening/geopackage_export.py`) writes parcel IDs and polygons, source-covered parcel footprints, and positive-area known constraint overlaps. Duplicate or overlapping constraints of the same type are unioned. Incidental parcel attributes such as owner names are deliberately excluded. Output paths must end in `.gpkg`; existing files are not overwritten. The tabular constraint matrix remains authoritative for negative results and unknown coverage because empty GeoPackage layers may be omitted.

The module currently does not write a single transactional report bundle, source metadata tables, map layouts, or the unknown-coverage geometry. It is a synthetic reference implementation, not a surveyed or regulatory GIS product. Do not infer a legally buildable area from the absence of mapped overlap.

## Auditable parcel deliverable bundle

The bundle module (`examples/12-environmental-screening/bundle.py`) coordinates the synthetic screening matrix, validated source register, GeoPackage, and `manifest.json` in a newly created directory. The manifest records the analysis CRS, parcel count, constraint result count, source count, filenames, byte lengths, and SHA-256 checksums. `verify_bundle` requires all four deliverables and their supported manifest as regular files in a flat directory. It rejects missing, added, modified, duplicate, or symlinked members and unlisted directories, including their nested files. An empty or incomplete bundle cannot verify. A source record is mandatory for each constraint type when building the bundle. It refuses to overwrite an existing bundle and attempts cleanup after an incomplete build.

**Integrity is not source authenticity:** A checksum detects changes after packaging but does not prove that a parcel boundary or environmental dataset is authoritative, complete, or current. The bundle includes the reviewer PNG described below. It does not provide cryptographic signatures or an atomic filesystem transaction. Do not use it as a regulatory decision product.

## Reviewer map

The bundle now includes `parcel_review_map.png`, an offline map showing GIS parcel boundaries, mapped constraints, and environmental source-coverage footprints. The view uses the padded parcel bounds, so regional source footprints and distant constraints cannot shrink the study area to an unreadable dot. These view limits do not change screening or exported geometries. Its legend and disclaimer distinguish screening from a surveyed or regulatory determination. The PNG is included in the SHA-256 manifest and is not a substitute for the accompanying GIS layers, source register, and parcel constraint matrix. The rendering does not imply that all constraint sources have the same positional accuracy or resolution. No client parcel data is included in this cookbook.

Screening, boundary review, export, and map labels use each input frame's active geometry column, including names other than `geometry`. Inputs are not renamed or mutated; an inactive metadata column named `geometry` is not substituted for the active geometry or included in the parcel export.
