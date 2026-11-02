# GIS workflow diagnostic demonstration

This synthetic example connects the cookbook's spatial processing patterns into
a reviewable business workflow: incoming location records become accepted data,
reason-coded rejects, and a reconciled QA summary.

## Run the example

From the repository root, after installing the dependencies:

```bash
python demos/workflow_qa.py demos/workflow-input.json /tmp/zqm-qa-report.json
python -m pytest tests/test_workflow_qa.py -q
```

On Windows, replace `/tmp/zqm-qa-report.json` with a writable output path outside
the repository. Expected summary: **8 input, 2 accepted, 6 rejected**.
All coordinates and records are synthetic; this is not a client case study.

## What the demonstration proves

- Every input row is accepted or rejected exactly once; multiple rejection
  reasons can attach to one row.
- All occurrences of a duplicate ID are rejected. IDs are exact strings;
  normalization and entity resolution require a separate business rule.
- Missing names, missing or unreadable geometry, non-point geometry, non-finite
  coordinates, and points outside the boundary are identified.
- The source CRS must be declared. The boundary uses that same CRS. The target
  analysis CRS must be projected and suitable for the client's actual location.
- The boundary rule includes points on its edge, evaluated after transformation.
  Polygon edges are transformed as supplied, without geodesic densification.
- Repeated runs with identical inputs and software produce identical bundles.
- Batch-contract failures and failed atomic replacement preserve the previous
  successful output. Accepted records and rejects publish together in one file.

## Read the output

The JSON bundle includes `summary`, `accepted`, `rejected`, input SHA-256, source
and analysis CRS, boundary policy, and software versions. Accepted geometries use
the declared **analysis CRS**. They are feature-shaped objects within a custom
bundle, not a standalone RFC 7946 GeoJSON file. Rejects retain the original row
and zero-based input position for correction.

An all-rejected batch still produces a valid QA report with zero accepted rows.
Success means processing completed, not that the data passed QA. A downstream
loader must enforce its own acceptance threshold before importing records.

This local, single-writer demonstration is not a multi-user ingestion service.
It does not provide authentication, retention enforcement, deduplication across
batches, CRS inference, automatic repairs, throughput guarantees, or power-loss
durability. Use authorized samples and define those requirements during discovery.

## Three-minute buyer walkthrough

1. Show the eight records and explain the intended input contract.
2. Run the command and inspect the two accepted records, including the edge point.
3. Review six rejects and their reasons; reconcile all eight input rows.
4. Rerun the command to show reproducibility. Use the tests to demonstrate that
   invalid batches cannot replace the last successful output.
5. Discuss the buyer's actual inputs, review steps, ownership, and failure costs.

No manual labor savings or client outcomes have been measured here. Benchmark
the buyer's actual workflow before estimating savings or promising performance.

## Apply it to a recurring workflow

ZQM Computing's proposed starting engagement is a **$1,500 GIS Workflow
Diagnostic**, covering one recurring process, up to three agreed representative
inputs, and one target output. Deliverables are a workflow map, labeled baseline
measurements or estimates, prioritized recommendations, and a separately scoped
implementation proposal. Target delivery is five business days after kickoff and
receipt of agreed inputs, subject to confirmed scope and availability.

To discuss fit, contact [ZQM Computing](mailto:zqmcomputing@gmail.com) with the
workflow, tools, frequency, and desired output. Do not send credentials or client
datasets in a public GitHub issue. Implementation and ongoing support are separate;
the diagnostic does not include professional certification or regulatory approval.

The examples remain MIT licensed. Paid services cover client-specific discovery,
integration, validation and handoff; purchasing services is not required to use
the open-source code.
