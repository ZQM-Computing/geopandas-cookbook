"""Benchmark indexed and vectorized point-in-polygon queries on synthetic data.

The benchmark separates spatial-index construction from query time, checks exact
matching positions (not only counts), warms both paths, and reports medians.
Timings are diagnostic and must be repeated on representative workloads before
being used to justify a production design.
"""
from __future__ import annotations

import argparse
import statistics
import time

import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import box

SEED = 20261024
FEATURE_COUNT = 20_000
REPEATS = 7


def positive_int(value: str) -> int:
    """Parse a strictly positive integer for benchmark controls."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse benchmark scale and repeat controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--features",
        type=positive_int,
        default=FEATURE_COUNT,
        help=f"synthetic point count (default: {FEATURE_COUNT:,})",
    )
    parser.add_argument(
        "--repeats",
        type=positive_int,
        default=REPEATS,
        help=f"timed repetitions per query path (default: {REPEATS})",
    )
    return parser.parse_args(argv)


def median_seconds(operation, repeats: int = REPEATS) -> float:
    """Return median elapsed time after one untimed warm-up."""
    operation()
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        operation()
        samples.append(time.perf_counter() - started)
    return statistics.median(samples)


def main(argv: list[str] | None = None) -> None:
    """Build deterministic points and compare equivalent spatial predicates."""
    args = parse_args(argv)
    rng = np.random.default_rng(SEED)
    xs = rng.uniform(-81.4, -80.7, args.features)
    ys = rng.uniform(28.9, 29.6, args.features)

    # Shapely 2 creates the point array in vectorized native code rather than
    # allocating one Python Point object per coordinate pair.
    points = gpd.GeoSeries(shapely.points(xs, ys), crs="EPSG:4326")
    area = box(-81.2, 29.1, -80.9, 29.4)

    index_started = time.perf_counter()
    spatial_index = points.sindex
    index_build_seconds = time.perf_counter() - index_started

    def indexed_query():
        return np.asarray(spatial_index.query(area, predicate="contains"), dtype=np.intp)

    def vectorized_scan():
        return np.flatnonzero(points.within(area).to_numpy())

    indexed_positions = np.sort(indexed_query())
    vectorized_positions = vectorized_scan()
    if not np.array_equal(indexed_positions, vectorized_positions):
        raise AssertionError(
            "Indexed and vectorized predicates returned different feature positions"
        )

    indexed_query_seconds = median_seconds(indexed_query, args.repeats)
    vectorized_scan_seconds = median_seconds(vectorized_scan, args.repeats)

    print(f"Features: {args.features:,}")
    print(f"Matches: {len(indexed_positions):,}")
    print(f"Seed: {SEED}")
    print(f"Repeats: {args.repeats}")
    print(f"GeoPandas: {gpd.__version__}")
    print(f"Shapely: {shapely.__version__}")
    print(f"Spatial-index build: {index_build_seconds:.6f}s")
    print(f"Indexed query median: {indexed_query_seconds:.6f}s")
    print(f"Vectorized scan median: {vectorized_scan_seconds:.6f}s")
    if indexed_query_seconds > 0:
        print(f"Query-only speedup: {vectorized_scan_seconds / indexed_query_seconds:.2f}x")
    print("Correctness: exact matching feature positions")


if __name__ == "__main__":
    main()
