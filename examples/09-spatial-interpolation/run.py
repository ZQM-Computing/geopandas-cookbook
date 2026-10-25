"""Inverse-distance weighting (IDW) on a small synthetic station network."""
import numpy as np
from shapely.geometry import Point

stations = [
    (Point(0, 0), 12.0),
    (Point(1000, 0), 18.0),
    (Point(0, 1000), 16.0),
    (Point(1000, 1000), 22.0),
]


def idw_estimate(location, sample_stations, power=2.0):
    """Estimate a value at a point using inverse-distance weighting.

    Exact station hits return the station value rather than dividing by zero.
    The power must be finite and strictly positive.
    """
    if not np.isfinite(power) or power <= 0:
        raise ValueError("power must be finite and greater than zero")
    if not sample_stations:
        raise ValueError("at least one station is required")

    distances = np.array(
        [location.distance(point) for point, _ in sample_stations], dtype=float
    )
    values = np.array([value for _, value in sample_stations], dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("station values must all be finite")

    exact = np.flatnonzero(distances == 0)
    if len(exact):
        # If duplicate stations occupy this exact location, average their values
        # rather than making the result depend on input order.
        return float(values[exact].mean())

    weights = 1.0 / distances**power
    return float(np.sum(values * weights) / np.sum(weights))


# Exercise the exact-station branch, which an interior-only grid would miss.
for point, value in stations:
    assert idw_estimate(point, stations) == value

try:
    idw_estimate(Point(500, 500), stations, power=0)
except ValueError:
    pass
else:
    raise AssertionError("IDW must reject a zero power")

grid = [(x, y) for y in (250, 500, 750) for x in (250, 500, 750)]
power = 2.0
station_values = [value for _, value in stations]
for x, y in grid:
    estimate = idw_estimate(Point(x, y), stations, power=power)
    assert np.isfinite(estimate)
    assert min(station_values) <= estimate <= max(station_values)
    print(f"({x:4d}, {y:4d}) -> {estimate:.2f}")
