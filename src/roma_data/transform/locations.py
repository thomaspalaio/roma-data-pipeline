"""
Location transformation for Roma Data Pipeline.

Aggregates and deduplicates location data from all sources.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


def transform_locations(config: "Config") -> int:
    """
    Transform and aggregate location data from all enabled sources.

    Each source's transform() method has already produced normalized records.
    This function aggregates them into a single locations.json file.

    Args:
        config: Pipeline configuration.

    Returns:
        Number of locations written.
    """
    all_locations: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()

    processed_dir = config.output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Collect locations from Pleiades
    if "pleiades" in config.sources:
        from roma_data.sources.pleiades import PleiadesSource
        source = PleiadesSource(config)
        try:
            locations = source.transform()
            for loc in locations:
                if loc["id"] not in seen_ids:
                    all_locations.append(loc)
                    seen_ids.add(loc["id"])
            print(f"  Pleiades: {len(locations)} locations")
        except FileNotFoundError as e:
            logger.warning(f"Pleiades data not found: {e}")

    # Collect locations from AWMC (provinces - separate handling)
    # Provinces go to provinces.json, not locations.json

    # Collect locations from ORBIS
    if "orbis" in config.sources:
        try:
            from roma_data.sources.orbis import ORBISSource
            source = ORBISSource(config)
            locations = source.transform()
            for loc in locations:
                if loc["id"] not in seen_ids:
                    all_locations.append(loc)
                    seen_ids.add(loc["id"])
            print(f"  ORBIS: {len(locations)} locations")
        except (FileNotFoundError, NotImplementedError) as e:
            logger.debug(f"ORBIS locations skipped: {e}")

    # Collect locations from ToposText
    if "topostext" in config.sources:
        try:
            from roma_data.sources.topostext import ToposTextSource
            source = ToposTextSource(config)
            locations = source.transform()
            for loc in locations:
                if loc["id"] not in seen_ids:
                    all_locations.append(loc)
                    seen_ids.add(loc["id"])
            print(f"  ToposText: {len(locations)} locations")
        except (FileNotFoundError, NotImplementedError) as e:
            logger.debug(f"ToposText locations skipped: {e}")

    # Sort by ID for deterministic output
    all_locations.sort(key=lambda x: x["id"])

    # Write to processed directory
    output_path = processed_dir / "locations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_locations, f, indent=2, ensure_ascii=False)

    print(f"\n  Total locations: {len(all_locations)}")
    logger.info(f"Wrote {len(all_locations)} locations to {output_path}")

    return len(all_locations)


def deduplicate_locations(locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate locations by coordinates and name.

    Uses a spatial and name-based matching strategy to merge
    duplicate entries from different sources.

    Args:
        locations: List of location records.

    Returns:
        Deduplicated list of locations.
    """
    # Simple deduplication by ID for now
    seen: Dict[str, Dict[str, Any]] = {}

    for loc in locations:
        loc_id = loc["id"]
        if loc_id not in seen:
            seen[loc_id] = loc
        else:
            # Merge additional data from duplicate
            existing = seen[loc_id]
            # Prefer non-null values
            for key, value in loc.items():
                if value is not None and existing.get(key) is None:
                    existing[key] = value

    return list(seen.values())
