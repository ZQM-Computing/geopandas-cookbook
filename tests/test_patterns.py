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



def test_geopackage_roundtrip_preserves_layer_schema_crs_and_geometry(tmp_path):
    """A GeoPackage round-trip preserves layer names, attributes, CRS, and geometry."""
    import geopandas as gpd
    from shapely.geometry import Point, box

    path = tmp_path / "contract.gpkg"
    sites = gpd.GeoDataFrame(
        {"site_id": [1, 2], "name": ["North", "South"]},
        geometry=[Point(-81.1, 29.3), Point(-81.0, 29.1)],
        crs="EPSG:4326",
    )
    zones = gpd.GeoDataFrame(
        {"zone_id": [10]},
        geometry=[box(-81.2, 29.0, -80.9, 29.4)],
        crs="EPSG:4326",
    )

    sites.to_file(path, layer="sites", driver="GPKG", index=False)
    zones.to_file(path, layer="zones", driver="GPKG", index=False)

    restored_sites = gpd.read_file(path, layer="sites")
    restored_zones = gpd.read_file(path, layer="zones")

    assert len(restored_sites) == 2
    assert len(restored_zones) == 1
    assert restored_sites.crs is not None and restored_sites.crs.to_epsg() == 4326
    assert restored_zones.crs is not None and restored_zones.crs.to_epsg() == 4326
    assert restored_sites["site_id"].tolist() == [1, 2]
    assert restored_sites["name"].tolist() == ["North", "South"]
    assert restored_zones["zone_id"].tolist() == [10]
    assert restored_sites.geometry.iloc[0].equals(sites.geometry.iloc[0])
    assert restored_zones.geometry.iloc[0].equals(zones.geometry.iloc[0])


def test_crs_transformation_roundtrip_preserves_coordinate_values():
    """Transforming through metric analysis CRSs and back should have bounded drift."""
    import geopandas as gpd
    from shapely.geometry import Point

    source = gpd.GeoDataFrame(
        {"asset_id": [1, 2]},
        geometry=[Point(-81.1, 29.2), Point(-80.9, 29.25)],
        crs="OGC:CRS84",
    )
    utm = source.to_crs("EPSG:32617")
    albers = utm.to_crs("EPSG:5070")
    restored = albers.to_crs("OGC:CRS84")

    assert utm.crs is not None and utm.crs.to_epsg() == 32617
    assert albers.crs is not None and albers.crs.to_epsg() == 5070
    assert utm.geometry.x.abs().min() > 100_000
    assert utm.geometry.x.abs().max() < 900_000

    drift_x = (source.geometry.x - restored.geometry.x).abs().max()
    drift_y = (source.geometry.y - restored.geometry.y).abs().max()
    assert max(drift_x, drift_y) < 1e-8


def test_readme_exists():
    """README.md exists."""
    assert (ROOT / "README.md").exists()


def test_license_exists():
    """LICENSE file exists."""
    assert (ROOT / "LICENSE").exists()
