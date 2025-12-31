"""
Data enrichment for Roma Data Pipeline.

Cross-links entities using spatial indexing and name matching.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


def enrich_all(config: Config) -> None:
    """
    Enrich data with cross-entity links.

    This stage:
    1. Builds a spatial index of locations
    2. Assigns province IDs to locations based on coordinates
    3. Links people and events to locations
    4. Creates junction tables (road_cities, event_participants)

    Args:
        config: Pipeline configuration.
    """
    processed_dir = config.output_dir / "processed"

    # Load locations
    locations = _load_json(processed_dir / "locations.json")
    if not locations:
        logger.info("No locations to enrich")
        return

    # Load provinces if available
    provinces = _load_json(processed_dir / "provinces.json")

    # Assign province IDs to locations (if provinces available)
    if provinces:
        print("  Enriching locations with province data...")
        locations = _assign_provinces(locations, provinces)
        _save_json(processed_dir / "locations.json", locations)
        print("    Assigned provinces to locations")

    # Create empty junction tables (will be populated by future enrichment)
    _save_json(processed_dir / "road_cities.json", [])
    _save_json(processed_dir / "event_participants.json", [])
    _save_json(processed_dir / "person_relationships.json", [])
    _save_json(processed_dir / "person_roles.json", [])

    logger.info("Enrichment complete")


def _load_json(path: Path) -> list[dict[str, Any]]:
    """Load JSON file, return empty list if not found."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: list[dict[str, Any]]) -> None:
    """Save data to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _assign_provinces(
    locations: list[dict[str, Any]],
    provinces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Assign province IDs to locations based on coordinates.

    Uses a simple centroid distance approach for now.
    A full implementation would use shapely for point-in-polygon tests.
    """
    # Build province centroids
    province_centroids: list[tuple[str, float, float]] = []
    for prov in provinces:
        if prov.get("centroid_lat") and prov.get("centroid_lon"):
            province_centroids.append((
                prov["id"],
                prov["centroid_lat"],
                prov["centroid_lon"],
            ))

    if not province_centroids:
        return locations

    # Assign nearest province to each location (simple approach)
    for loc in locations:
        if loc.get("province_id"):
            continue  # Already assigned

        lat, lon = loc["latitude"], loc["longitude"]
        best_prov = None
        best_dist = float("inf")

        for prov_id, plat, plon in province_centroids:
            dist = (lat - plat) ** 2 + (lon - plon) ** 2
            if dist < best_dist:
                best_dist = dist
                best_prov = prov_id

        if best_prov and best_dist < 100:  # Within ~10 degrees
            loc["province_id"] = best_prov

    return locations
