"""
Road transformation for Roma Data Pipeline.

Transforms road data from Itiner-e source.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


def transform_roads(config: "Config") -> int:
    """
    Transform road data from Itiner-e source.

    Args:
        config: Pipeline configuration.

    Returns:
        Number of roads written.
    """
    all_roads: List[Dict[str, Any]] = []

    processed_dir = config.output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Collect roads from Itiner-e
    if "itinere" in config.sources:
        try:
            from roma_data.sources.itinere import ItinereSource
            source = ItinereSource(config)
            roads = source.transform()
            all_roads.extend(roads)
            print(f"  Itiner-e: {len(roads)} roads")
        except (FileNotFoundError, NotImplementedError) as e:
            logger.debug(f"Itiner-e roads skipped: {e}")

    # Sort by ID for deterministic output
    all_roads.sort(key=lambda x: x["id"])

    # Write to processed directory
    output_path = processed_dir / "roads.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_roads, f, indent=2, ensure_ascii=False)

    if all_roads:
        print(f"\n  Total roads: {len(all_roads)}")
    logger.info(f"Wrote {len(all_roads)} roads to {output_path}")

    return len(all_roads)
