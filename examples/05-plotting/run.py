"""Export a static map and, when Folium is installed, an interactive map."""
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point, box

out_dir = Path("build")
out_dir.mkdir(exist_ok=True)
areas = gpd.GeoDataFrame(
    {"area": ["North", "South"]},
    geometry=[box(-81.2, 29.2, -80.9, 29.4), box(-81.2, 29.0, -80.9, 29.2)],
    crs="EPSG:4326",
)
sites = gpd.GeoDataFrame(
    {"site": ["A", "B", "C"]},
    geometry=[Point(-81.1, 29.3), Point(-81.0, 29.1), Point(-80.95, 29.25)],
    crs="EPSG:4326",
)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Install plotting support with: pip install matplotlib") from exc

ax = areas.plot(color="whitesmoke", edgecolor="black", figsize=(7, 5))
sites.plot(ax=ax, color="darkred", markersize=35)
ax.set_title("Synthetic service areas and sites")
ax.set_axis_off()
figure_path = out_dir / "geopandas-sites.png"
ax.figure.savefig(figure_path, dpi=140, bbox_inches="tight")
plt.close(ax.figure)
print(f"Static map saved to {figure_path}")

try:
    interactive = sites.explore(column="site", tooltip=["site"])
    html_path = out_dir / "geopandas-sites.html"
    interactive.save(html_path)
    print(f"Interactive map saved to {html_path}")
except (ImportError, ModuleNotFoundError):
    print("Interactive map skipped; install Folium with: pip install folium")
