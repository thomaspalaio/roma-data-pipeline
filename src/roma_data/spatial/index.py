"""Spatial index for location matching - stub."""

from __future__ import annotations

from typing import Any


class SpatialIndex:
    """
    Grid-based spatial index for fast nearest-neighbor lookups.

    Used for matching coordinates to locations and entity linking.
    """

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
        """Find nearest location within distance."""
        # TODO: Implement nearest neighbor search
        raise NotImplementedError("Spatial index not yet implemented")

    def find_within(
        self, lat: float, lon: float, radius_km: float
    ) -> list[dict[str, Any]]:
        """Find all locations within radius."""
        # TODO: Implement radius search
        raise NotImplementedError("Spatial index not yet implemented")

    def _get_cell(self, lat: float, lon: float) -> tuple[int, int]:
        """Get grid cell for coordinates."""
        return (int(lat / self.cell_size), int(lon / self.cell_size))
