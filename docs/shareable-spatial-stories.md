# Shareable geospatial stories with reproducible evidence

**Status: technical demonstration and editorial playbook, not a claim of
observed environmental change or a client case study.**

This is a ZQM Computing education and professional-lead-generation pattern.
Game concepts and quests belong to the separate ZQM Labs brand.

## Example: illustrated before/after spatial comparison

Run from the repository root after installing project dependencies:

    python demos/land_change_story.py --output-dir /tmp/zqm-land-change

On Windows, use an accessible local output directory instead of /tmp.

Outputs:

- synthetic-land-change.png — side-by-side scenario visualization
- synthetic-land-change.metrics.json — source label, units, scenario area,
  gross gain, gross loss, net change and method

The study region and coverage geometries are intentionally constructed
from Shapely shapes on a **dimensionless synthetic planar grid**. They have
no coordinate reference system, real dates, satellite pixels, parcel
identifiers, proprietary data, or physical units. The word "change" means
a topological comparison of two **illustrative scenarios**, not a measured
real-world event. The toy figures produce Scenario A = 12, Scenario B = 23,
gross gain = 11, gross loss = 0 square grid units.

The companion JSON must accompany any distribution of the image. Never
crop out the illustrative-source label or describe the graphic as observed
development, land-cover loss, or a real property screening result.

## Adaptation to real Earth-change content

To turn this into a factual environmental story, establish a new,
separately-reviewed workflow with:

1. Legal access, attribution, licensing and redistribution rights for all
   imagery and boundaries.
2. Geographic coverage, acquisition dates, cloud/shadow quality and sensor
   comparability, with disclosed exclusions.
3. Explicit source and analysis CRS, appropriate projected area units,
   resolution, pixel alignment and uncertainty.
4. A declared classifier or change-detection method, a reference sample
   or ground truth, and accuracy reporting before making measured claims.
5. Reproducible artifact hashes, exact software versions, raw input
   provenance, and a public-safe visual narrative.
6. Human review, accessibility text, and protection of private parcel,
   customer, and personally identifying information.

The synthetic demo intentionally does **not** implement satellite change
detection. A future field pipeline must not inherit its illustrative
metrics or imply it validates environmental or regulatory compliance.

## Distribution formats for ZQM Computing

- A quick annotated comparison image, with a question followed by a
  factual, sourced reveal (once real data has passed validation).
- A reproducible GIS explanation on GitHub, linked to method and sources.
- An AI-vs-GIS-expert validation story that exposes incorrect projection,
  area, join or provenance assumptions with deterministic test evidence.
- A professional workflow diagnostic offering: link to the existing
  QA demo and preliminary environmental screening specification, stating
  deliverable scope and excluding certification or regulatory approval.

Treat views, comments, click-throughs, GitHub reuse and qualified service
inquiries as separate metrics. Never equate social attention with verified
project demand. Do not invent baseline metrics or frame synthetic output
as customer results. Schedule and publish content independently from the
production GIS operations stack.
