"""Benchmark spatial-index crossover across selectivities and point distributions.

The benchmark separates index construction from query time, verifies exact
matching positions, warms both paths, and reports medians. Synthetic uniform,
clustered, and mixed distributions expose sensitivity to data layout; they are
not substitutes for representative production geometries.
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
QUERY_AREAS = {
    "selective": box(-81.085, 29.415, -81.015, 29.485),
    "moderate": box(-81.2, 29.1, -80.9, 29.4),
    "broad": box(-81.36, 28.94, -80.74, 29.56),
}
DISTRIBUTIONS = ("uniform", "clustered", "mixed")


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
    """Parse benchmark scale, repeat, and distribution controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=positive_int, default=FEATURE_COUNT)
    parser.add_argument("--repeats", type=positive_int, default=REPEATS)
    parser.add_argument("--distribution", choices=DISTRIBUTIONS, default="uniform")
    return parser.parse_args(argv)


def generate_coordinates(
    features: int, distribution: str, seed: int = SEED
) -> tuple[np.ndarray, np.ndarray]:
    """Generate reproducible bounded coordinates for a named synthetic layout."""
    if features <= 0:
        raise ValueError("features must be greater than zero")
    if distribution not in DISTRIBUTIONS:
        raise ValueError(f"distribution must be one of {DISTRIBUTIONS}")

    rng = np.random.default_rng(seed)
    bounds = (-81.4, -80.7, 28.9, 29.6)
    if distribution == "uniform":
        xs = rng.uniform(bounds[0], bounds[1], features)
        ys = rng.uniform(bounds[2], bounds[3], features)
    else:
        centers = np.array([
            [-81.25, 29.15], [-80.85, 29.15],
            [-81.25, 29.55], [-81.05, 29.45],
        ])
        if distribution == "clustered":
            cluster_count = features
        else:
            cluster_count = int(features * 0.7)
        choices = rng.integers(0, len(centers), cluster_count)
        clustered = centers[choices] + rng.normal(0, 0.035, (cluster_count, 2))
        if distribution == "mixed":
            uniform_count = features - cluster_count
            uniform = np.column_stack((
                rng.uniform(bounds[0], bounds[1], uniform_count),
                rng.uniform(bounds[2], bounds[3], uniform_count),
            ))
            coordinates = np.vstack((clustered, uniform))
            rng.shuffle(coordinates, axis=0)
        else:
            coordinates = clustered
        xs = np.clip(coordinates[:, 0], bounds[0], bounds[1])
        ys = np.clip(coordinates[:, 1], bounds[2], bounds[3])
    return xs, ys


def median_seconds(operation, repeats: int) -> float:
    """Return median elapsed time after one untimed warm-up."""
    operation()
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        operation()
        samples.append(time.perf_counter() - started)
    return statistics.median(samples)


def main(argv: list[str] | None = None) -> None:
    """Compare equivalent indexed and vectorized predicates."""
    args = parse_args(argv)
    xs, ys = generate_coordinates(args.features, args.distribution)
    points = gpd.GeoSeries(shapely.points(xs, ys), crs="EPSG:4326")

    index_started = time.perf_counter()
    spatial_index = points.sindex
    index_build_seconds = time.perf_counter() - index_started

    print(f"Features: {args.features:,}")
    print(f"Distribution: {args.distribution}")
    print(f"Seed: {SEED}")
    print(f"Repeats: {args.repeats}")
    print(f"GeoPandas: {gpd.__version__}")
    print(f"Shapely: {shapely.__version__}")
    print(f"NumPy: {np.__version__}")
    print(f"Spatial-index build: {index_build_seconds:.6f}s")

    for label, area in QUERY_AREAS.items():
        def indexed_query():
            return np.asarray(
                spatial_index.query(area, predicate="contains"), dtype=np.intp
            )

        def vectorized_scan():
            return np.flatnonzero(points.within(area).to_numpy())

        indexed_positions = np.sort(indexed_query())
        vectorized_positions = vectorized_scan()
        if not np.array_equal(indexed_positions, vectorized_positions):
            raise AssertionError(
                f"{label}: indexed and vectorized predicates returned "
                "different feature positions"
            )

        indexed_seconds = median_seconds(indexed_query, args.repeats)
        scan_seconds = median_seconds(vectorized_scan, args.repeats)
        match_fraction = len(indexed_positions) / args.features
        ratio = scan_seconds / indexed_seconds if indexed_seconds > 0 else float("nan")

        print(f"\\nQuery: {label}")
        print(f"Matches: {len(indexed_positions):,} ({match_fraction:.2%})")
        print(f"Indexed query median: {indexed_seconds:.6f}s")
        print(f"Vectorized scan median: {scan_seconds:.6f}s")
        print(f"Scan/indexed ratio: {ratio:.2f}x")
        print("Correctness: exact matching feature positions")


if __name__ == "__main__":
    main()
