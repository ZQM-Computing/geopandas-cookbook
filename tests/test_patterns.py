"""Tests for geopandas-cookbook examples."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = ROOT / "examples"
EXPECTED_EXAMPLES = 12


def test_examples_present():
    """Fail if advertised examples are missing or duplicated."""
    assert EXAMPLES_DIR.is_dir(), "examples/ directory is missing"
    found = sorted(EXAMPLES_DIR.glob("*/run.py"))
    assert len(found) == EXPECTED_EXAMPLES, (
        f"Expected exactly {EXPECTED_EXAMPLES} runnable examples, found {len(found)}: "
        f"{[path.relative_to(ROOT).as_posix() for path in found]}"
    )
    assert len({path.parent.name for path in found}) == EXPECTED_EXAMPLES


def test_python_syntax():
    """Every example has valid Python syntax."""
    for py_file in sorted(EXAMPLES_DIR.glob("*/run.py")):
        subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )


def test_examples_execute():
    """Smoke-run all examples with synthetic data; PostGIS skips unless configured."""
    env = os.environ.copy()
    env.pop("GEOPANDAS_POSTGIS_URL", None)
    for py_file in sorted(EXAMPLES_DIR.glob("*/run.py")):
        result = subprocess.run(
            [sys.executable, str(py_file)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (
            f"{py_file.relative_to(ROOT)} failed with exit code {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_readme_exists():
    """README.md exists."""
    assert (ROOT / "README.md").exists()


def test_license_exists():
    """LICENSE file exists."""
    assert (ROOT / "LICENSE").exists()
