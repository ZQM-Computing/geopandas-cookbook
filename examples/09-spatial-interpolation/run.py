"""Inverse-distance weighting (IDW) on a small synthetic station network."""
import numpy as np
from shapely.geometry import Point

stations = [
    (Point(0, 0), 12.0),
    (Point(1000, 0), 18.0),
    (Point(0, 1000), 16.0),
    (Point(1000, 1000), 22.0),
]
grid = [(x, y) for y in (250, 500, 750) for x in (250, 500, 750)]
power = 2.0
for x, y in grid:
    distances = np.array([Point(x, y).distance(point) for point, _ in stations])
    values = np.array([value for _, value in stations])
    exact = np.flatnonzero(distances == 0)
    estimate = float(values[exact[0]]) if len(exact) else float(
        np.sum(values / distances**power) / np.sum(1.0 / distances**power)
    )
    print(f"({x:4d}, {y:4d}) -> {estimate:.2f}")
