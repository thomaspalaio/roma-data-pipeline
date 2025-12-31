"""
Events transformation for Roma Data Pipeline.

Transforms event data from Wikidata source.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


def transform_events(config: Config) -> int:
    """
    Transform event data from Wikidata source.

    Args:
        config: Pipeline configuration.

    Returns:
        Number of events written.
    """
    all_events: list[dict[str, Any]] = []

    processed_dir = config.output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Collect events from Wikidata
    if "wikidata" in config.sources:
        try:
            from roma_data.sources.wikidata import WikidataSource
            source = WikidataSource(config)
            events = source.transform_events()
            all_events.extend(events)
            print(f"  Wikidata: {len(events)} events")
        except (FileNotFoundError, NotImplementedError, AttributeError) as e:
            logger.debug(f"Wikidata events skipped: {e}")

    # Sort by ID for deterministic output
    all_events.sort(key=lambda x: x["id"])

    # Write to processed directory
    output_path = processed_dir / "events.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)

    if all_events:
        print(f"\n  Total events: {len(all_events)}")
    logger.info(f"Wrote {len(all_events)} events to {output_path}")

    return len(all_events)
