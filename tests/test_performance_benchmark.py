"""Scale-control contracts for the GeoPandas performance benchmark."""
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "examples" / "06-performance" / "run.py"


def test_benchmark_accepts_explicit_large_feature_counts_and_repeats():
    namespace = runpy.run_path(str(BENCHMARK))
    args = namespace["parse_args"](["--features", "1000000", "--repeats", "3"])
    assert args.features == 1_000_000
    assert args.repeats == 3


def test_benchmark_rejects_nonpositive_scale():
    import argparse

    namespace = runpy.run_path(str(BENCHMARK))
    for value in ("0", "-1"):
        try:
            namespace["positive_int"](value)
        except argparse.ArgumentTypeError:
            pass
        else:
            raise AssertionError(f"nonpositive benchmark value accepted: {value}")
