"""Spatial index for location matching."""

from __future__ import annotations

import math
from typing import Any


class SpatialIndex:
    """
    Grid-based spatial index for fast nearest-neighbor lookups.

    Used for matching coordinates to locations and entity linking.
    """

    # Earth radius in km for distance calculations
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, cell_size: float = 1.0) -> None:
        """
        Initialize spatial index.

        Args:
            cell_size: Grid cell size in degrees (default: 1.0 = ~111km)
        """
        self.cell_size = cell_size
        self._grid: dict[tuple[int, int], list[dict[str, Any]]] = {}

    def add(self, lat: float, lon: float, data: dict[str, Any]) -> None:
        """Add a location to the index."""
        cell = self._get_cell(lat, lon)
        if cell not in self._grid:
            self._grid[cell] = []
        self._grid[cell].append({"lat": lat, "lon": lon, **data})

    def find_nearest(
        self, lat: float, lon: float, max_distance_km: float = 50.0
    ) -> dict[str, Any] | None:
        """
        Find nearest location within distance using grid-based search.

        Args:
            lat: Latitude to search from
            lon: Longitude to search from
            max_distance_km: Maximum search radius in kilometers

        Returns:
            Nearest location dict or None if nothing found within distance
        """
        # Convert max distance to approximate degree range
        degree_range = max_distance_km / 111.0  # ~111km per degree
        cells_to_check = int(math.ceil(degree_range / self.cell_size)) + 1

        center_cell = self._get_cell(lat, lon)
        nearest: dict[str, Any] | None = None
        nearest_dist = float("inf")

        # Check surrounding cells
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell not in self._grid:
                    continue

                for location in self._grid[cell]:
                    dist = self._haversine_distance(
                        lat, lon, location["lat"], location["lon"]
                    )
                    if dist < nearest_dist and dist <= max_distance_km:
                        nearest_dist = dist
                        nearest = location

        return nearest

    def find_within(
        self, lat: float, lon: float, radius_km: float
    ) -> list[dict[str, Any]]:
        """
        Find all locations within radius.

        Args:
            lat: Latitude to search from
            lon: Longitude to search from
            radius_km: Search radius in kilometers

        Returns:
            List of locations within the radius
        """
        degree_range = radius_km / 111.0
        cells_to_check = int(math.ceil(degree_range / self.cell_size)) + 1

        center_cell = self._get_cell(lat, lon)
        results: list[dict[str, Any]] = []

        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell not in self._grid:
                    continue

                for location in self._grid[cell]:
                    dist = self._haversine_distance(
                        lat, lon, location["lat"], location["lon"]
                    )
                    if dist <= radius_km:
                        results.append(location)

        return results

    def _get_cell(self, lat: float, lon: float) -> tuple[int, int]:
        """Get grid cell for coordinates."""
        return (int(lat / self.cell_size), int(lon / self.cell_size))

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate haversine distance between two points in kilometers."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS_KM * c
