# Spatial AI evaluation — open, offline sanity checks

This is a **model-agnostic demonstration harness**, not a public ranking of
Claude, GPT, Gemini, GeoAI agents or commercial systems. It uses six small,
synthetic GIS reasoning questions with deterministic, reviewable answers:
projected area, planar distance, polygon boundary inclusion, spatial-join
cardinality, geographic-CRS area handling and missing imagery coverage.
There is no image geolocation, API key, model API call, real-location input,
private dataset, network request, or automated agent integration.

## Run

From this cookbook's root:

```bash
python demos/spatial_ai_arena.py --questions
python demos/spatial_ai_arena.py --score /path/to/answers.json
python -m pytest -q tests/test_spatial_ai_arena.py
```

Example submission (the displayed answer is intentionally incorrect):

```json
{
  "run_label": "manual-demo",
  "predictions": [
    {"task_id": "projected_rectangle_area", "answer": 20}
  ]
}
```

The output includes each task's pass/fail/unanswered state, attempted count,
total, and overall score (missing answers count as unanswered). The model or
operator name is self-reported. The answer key is visible in the source, so
results are **not a blind benchmark**. Do not rank providers or publish
superlatives from a hand-entered result. The harness verifies the evaluator,
not a deployed LLM's performance.

## Before any genuine leaderboard

1. Fix datasets, golden outputs, license, evaluation scope and task weights
   before running models. Include CRS and units in prompts and answers.
2. Keep a blinded held-out evaluation set, prohibit benchmark-specific prompt
   leakage, and version prompts and adjudication. A public tutorial set alone
   is insufficient for independent performance claims.
3. Record exact model, reasoning configuration, agent harness, tool permissions,
   tool/environment versions, attempts, error handling, time and cost. Only
   compare results under equivalent task and tool conditions.
4. Include incomplete runs and refusals. Publish denominator, confidence,
   model coverage, task-level differences, and limitations; never invent ranks.
5. Use synthetic, owned, or expressly licensed remote sensing material. The
   photo-geolocation trend carries substantial location-privacy risks. Do
   not accept private third-party photos or build a route to locate people,
   homes, or nonpublic facilities.
6. Distinguish vendor or author reported benchmarks from independent
   replication. Axis Spatial and Google Research publish named evaluation
   methodologies, but their headline results should not be copied without
   verification of versions, tasks and experimental conditions.

## Verified external starting points (checked 2026-11-06)

- [Axis Spatial methodology](https://www.axisspatial.com/arena/methodology)
- [Google Research geospatial reasoning agent](https://research.google/blog/putting-earth-ai-to-work-geospatial-agents-for-our-planets-biggest-challenges/)
- [Bellingcat photo geolocation evaluation](https://www.bellingcat.com/resources/2026/10/22/can-llms-supercharge-geolocations-our-tests-show-big-improvements-but-humans-remain-key/)

The references contextualize a research topic; none are currently wired as
executable external dependencies or imply licensed data access.

## Communication format

Publish a grounded "AI versus reference GIS calculation" card with the
synthetic question, the model's answer (with authorized attribution), the
reference result, and an explicit pass/fail plus tool/environment provenance.
If a result is incomplete, show that. Route genuine professional inquiries to
the existing GIS workflow diagnostic rather than suggesting an unsupported
GeoAI product or a definitive AI ranking.
