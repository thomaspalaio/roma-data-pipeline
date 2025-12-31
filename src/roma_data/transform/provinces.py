"""
Province transformation for Roma Data Pipeline.

Transforms province boundary data from AWMC source.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


def transform_provinces(config: Config) -> int:
    """
    Transform province data from AWMC source.

    Args:
        config: Pipeline configuration.

    Returns:
        Number of provinces written.
    """
    all_provinces: list[dict[str, Any]] = []

    processed_dir = config.output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Collect provinces from AWMC
    if "awmc" in config.sources:
        try:
            from roma_data.sources.awmc import AWMCSource
            source = AWMCSource(config)
            provinces = source.transform()
            all_provinces.extend(provinces)
            print(f"  AWMC: {len(provinces)} provinces")
        except (FileNotFoundError, NotImplementedError) as e:
            logger.debug(f"AWMC provinces skipped: {e}")

    # Sort by start_year and ID
    all_provinces.sort(key=lambda x: (x.get("start_year", 0), x["id"]))

    # Write to processed directory
    output_path = processed_dir / "provinces.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_provinces, f, indent=2, ensure_ascii=False)

    if all_provinces:
        print(f"\n  Total provinces: {len(all_provinces)}")
    logger.info(f"Wrote {len(all_provinces)} provinces to {output_path}")

    return len(all_provinces)
