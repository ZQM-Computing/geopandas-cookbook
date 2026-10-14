# Security policy

## Supported version

Security fixes are applied to the `main` branch. This repository contains GeoPandas/Shapely example code; it is not a hosted service.

## Reporting a vulnerability

Email **zqmcomputing@gmail.com** with the subject `geopandas-patterns security` if you find a vulnerability in the example code or workflow configuration. Please do not open a public issue for a sensitive report.

Include the affected file, the impact you observed, and reproduction steps when available.

## Data note

Examples read local files with synthetic data. When adapting a pattern to your own data, keep an eye on file paths — a notebook or script that worked on a sample can overwrite real outputs if you point it at a production directory without checking.
