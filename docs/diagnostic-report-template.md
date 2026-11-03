# GIS Workflow Diagnostic — Client Report Template

> **Template only.** Replace every `[placeholder]` with evidence from an authorized
> engagement. Do not treat illustrative structure as observed client results.

## Engagement control

| Field | Value |
| --- | --- |
| Client / project | [Client and workflow] |
| Workflow owner | [Person authorized to confirm process and results] |
| Diagnostic date and revision | [Date, report version] |
| Consultant / contracting identity | [Contracting legal identity, contact] |
| Agreed workflow | [One recurring workflow, defined start and end] |
| Representative inputs | [Up to three agreed datasets; formats, sizes, rights] |
| Target deliverable | [One output and acceptance owner] |
| Evidence access | [Authorized samples/screenshare; sensitive data exclusions] |
| Retention / deletion | [Agreed handling, secure storage, deletion date] |
| Scope deviations approved | [None, or approved change order] |

This report is a scoped preliminary workflow review, not a certified survey,
engineering opinion, environmental site assessment, or regulatory determination.

## 1. Process map and handoffs

Describe current-state steps *before* prescribing automation. Attach a diagram
when its meaning cannot be adequately captured by the table.

| Step | Owner | Input / system | Transformation | Output / handoff | Failure or rework mode | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Role] | [Source, format] | [Action] | [Next step] | [Observed issue] | [Interview, run log, sample] |
| 2 | [Role] | [Source, format] | [Action] | [Next step] | [Observed issue] | [Interview, run log, sample] |

Flag every unverifiable assertion as **unconfirmed** rather than silently
filling the gap. State which workflows, systems, and datasets were excluded.

## 2. Baseline and rework evidence

| Metric | Current value | Unit / sample | Evidence type | Source and date |
| --- | --- | --- | --- | --- |
| Runs per month | [Unknown until verified] | [Runs] | [Observed / staff estimate / unknown] | [Source] |
| Staff time per run | [Unknown] | [Hours] | [Observed / estimate / unknown] | [Source] |
| Rework rate | [Unknown] | [Affected runs / total] | [Observed / estimate / unknown] | [Source] |
| End-to-end elapsed time | [Unknown] | [Business hours or days] | [Observed / estimate / unknown] | [Source] |
| Cost per hour | [Client-supplied only] | [Currency / hour] | [Finance assumption / unknown] | [Source] |

**Current monthly labor hours:** runs/month × labor hours/run, only when
both inputs are defensible. If estimating benefits, give a sensitivity range
and identify every assumption.

Capacity released is **not automatically cash saved**. Include implementation,
licenses, hosting, QA, human review, maintenance and support before suggesting
payback. Do not calculate ROI if there is no credible baseline.

## 3. Data and spatial QA observations

Record pass/fail/unknown for each applicable control:

| Control | Result | Evidence / required follow-up |
| --- | --- | --- |
| Ownership, permission and lawful use | [Pass / fail / unknown] | [Source authorization] |
| Input schema / stable feature identifier | [Pass / fail / unknown] | [Fields and key policy] |
| Explicit CRS / axis order / projection units | [Pass / fail / unknown] | [CRS and transformation checks] |
| Null, duplicate and invalid geometry handling | [Pass / fail / unknown] | [Reason-coded examples] |
| Boundary rule and precision / tolerance | [Pass / fail / unknown] | [Includes/excludes edge records] |
| Input = accepted + rejected reconciliation | [Pass / fail / unknown] | [Actual counts and logs] |
| Output schema, expected values and provenance | [Pass / fail / unknown] | [Version, hashes, sample] |
| Failure recovery / prior output preservation | [Pass / fail / unknown] | [Rollback and replay procedure] |
| Security, retention and access-control needs | [Pass / fail / unknown] | [Data classification and owners] |

For a *synthetic* demonstration, cite
[workflow diagnostic demo](workflow-diagnostic.md). Its passing tests are
evidence of the sample contract, **not** evidence that client data or systems
already satisfy these controls.

## 4. Opportunities and recommendations

| Priority | Candidate change | Value hypothesis | Dependencies | Human review retained | Evidence / confidence |
| --- | --- | --- | --- | --- | --- |
| [P0/P1/P2] | [Specific step] | [Measured burden or explicitly labeled hypothesis] | [People, licenses, data] | [Who approves] | [Observed / estimate / unknown] |

Possible conclusions are **automate**, **standardize but retain manual approval**,
**investigate further**, or **do not automate**. Explain trade-offs, rather than
turning every finding into a software sale.

## 5. Optional implementation scope (separately priced)

- **Objective and output:** [One measurable workflow outcome].
- **Included:** [Inputs, transformations, integration endpoints, tests, documentation].
- **Excluded:** [Production credential acquisition, data cleanup, fieldwork, additional systems,
  certification, regulatory decisions, 24/7 support unless separately contracted].
- **Prerequisites and assumptions:** [Authorized environment, input quality, decision owner].
- **Milestones and payment gates:** [Milestone, deliverable, client approval].
- **Acceptance tests:** [Concrete input fixtures, expected outputs, schema/CRS checks,
  duplicate rejection, error recovery and reconciliation].
- **Recovery:** [Rollback, last-good-output preservation and repeat procedure].
- **Ownership and maintenance:** [Code, data, hosting, support windows, handoff].
- **Total cost assumptions:** [Build, infrastructure, software, review, maintenance].
- **Go/no-go decision:** [Client approval after reviewing evidence].

A diagnostic fee covers the report itself; it does not include implementation
or promise an automatic implementation discount.

## 6. Findings review and clarification

| Item | Owner | Decision / correction | Due date |
| --- | --- | --- | --- |
| [Open item] | [Name or role] | [Decision] | [Date] |

Present the report in a 45-minute findings review. Consolidate one clarification
round within five business days of report delivery, as stated in the launch kit.
Additional analysis, datasets, or systems require agreement on changed scope.

**Client acknowledgment:** [Name / role / date / approved scope and residual risks].

---

**Confidentiality:** Do not commit client inputs, screenshots, identifiers,
pricing agreements, credentials or completed client reports to this public
repository. Keep only synthetic examples and reusable templates here.
