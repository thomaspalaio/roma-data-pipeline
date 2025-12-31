"""
People transformation for Roma Data Pipeline.

Transforms people data from Wikidata source.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


def transform_people(config: "Config") -> int:
    """
    Transform people data from Wikidata source.

    Args:
        config: Pipeline configuration.

    Returns:
        Number of people written.
    """
    all_people: List[Dict[str, Any]] = []

    processed_dir = config.output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Collect people from Wikidata
    if "wikidata" in config.sources:
        try:
            from roma_data.sources.wikidata import WikidataSource
            source = WikidataSource(config)
            people = source.transform_people()
            all_people.extend(people)
            print(f"  Wikidata: {len(people)} people")
        except (FileNotFoundError, NotImplementedError, AttributeError) as e:
            logger.debug(f"Wikidata people skipped: {e}")

    # Sort by ID for deterministic output
    all_people.sort(key=lambda x: x["id"])

    # Write to processed directory
    output_path = processed_dir / "people.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_people, f, indent=2, ensure_ascii=False)

    if all_people:
        print(f"\n  Total people: {len(all_people)}")
    logger.info(f"Wrote {len(all_people)} people to {output_path}")

    return len(all_people)
