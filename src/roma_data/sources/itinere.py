"""
Itiner-e Roman Roads data source.

Downloads and processes Roman road GeoJSON from Itiner-e.org.
Note: Itiner-e may require manual download due to site restrictions.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import requests

from roma_data.constants import CONFIDENCE_MAP, ITINERE_DOWNLOAD_URL, ROAD_TYPE_MAP
from roma_data.sources.base import DataSource

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


class ItinereSource(DataSource):
    """Data source for Itiner-e Roman roads."""

    name = "itinere"
    description = "Itiner-e Roman Road Network"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.itinere_file = self.raw_dir / "itinere_roads.geojson"

    def download(self) -> int:
        """
        Download Itiner-e road data.

        Note: The Itiner-e download endpoint may not work directly.
        If automatic download fails, users should manually download from:
        https://itiner-e.org/route-segments/download

        Returns:
            Number of road segments (0 if download failed).
        """
        self.ensure_dirs()
        self.itinere_file.parent.mkdir(parents=True, exist_ok=True)

        # Check cache
        if self.config.cache_downloads and self.itinere_file.exists():
            logger.info(f"Using cached Itiner-e data: {self.itinere_file}")
            with open(self.itinere_file, encoding="utf-8") as f:
                data = json.load(f)
            return len(data.get("features", []))

        print("  Attempting download from itiner-e.org...")
        print("  Note: This may require manual download if the site has changed.")

        try:
            response = requests.get(ITINERE_DOWNLOAD_URL, timeout=60, allow_redirects=True)
            response.raise_for_status()

            # Check if we got JSON data
            content_type = response.headers.get("content-type", "")
            text = response.text.strip()

            if "json" in content_type or text.startswith("{"):
                # Handle both standard GeoJSON and NDJSON (newline-delimited JSON)
                if text.startswith('{"type":"FeatureCollection"'):
                    # Standard GeoJSON FeatureCollection
                    data = json.loads(text)
                else:
                    # NDJSON format - each line is a Feature
                    features = []
                    for line in text.split("\n"):
                        line = line.strip()
                        if line:
                            try:
                                feature = json.loads(line)
                                if feature.get("type") == "Feature":
                                    features.append(feature)
                            except json.JSONDecodeError:
                                continue
                    data = {"type": "FeatureCollection", "features": features}

                # Save as standard GeoJSON
                with open(self.itinere_file, "w", encoding="utf-8") as f:
                    json.dump(data, f)

                count = len(data.get("features", []))
                print(f"  Downloaded: {count} road segments")
                return count
            else:
                print("  Direct download not available (site may require browser download)")
                print("  Please download manually from https://itiner-e.org/route-segments/download")
                print(f"  Save as: {self.itinere_file}")
                return 0

        except requests.RequestException as e:
            logger.warning(f"Itiner-e download failed: {e}")
            print(f"  Download failed: {e}")
            print("  Please download manually from https://itiner-e.org/route-segments/download")
            print(f"  Save as: {self.itinere_file}")
            return 0

    def transform(self) -> list[dict[str, Any]]:
        """
        Transform Itiner-e road data to processed format.

        Returns:
            List of road records.
        """
        if not self.itinere_file.exists():
            logger.info("Itiner-e data not found - skipping roads transform")
            return []

        with open(self.itinere_file, encoding="utf-8") as f:
            data = json.load(f)

        features = data.get("features", [])
        roads: list[dict[str, Any]] = []

        for i, feature in enumerate(features):
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            if geometry.get("type") not in ("LineString", "MultiLineString"):
                continue

            # Extract properties
            name = properties.get("name") or properties.get("ROAD_NAME")
            road_type = properties.get("type", "secondary")
            confidence = properties.get("certainty", "probable")

            # Map types and confidence
            mapped_type = ROAD_TYPE_MAP.get(road_type, ROAD_TYPE_MAP.get("default", "secondary"))
            mapped_confidence = CONFIDENCE_MAP.get(confidence, CONFIDENCE_MAP.get("default", "probable"))

            road = {
                "id": f"itinere_{i}",
                "name": name,
                "name_latin": name,
                "path_geojson": json.dumps(geometry),
                "construction_year": None,
                "abandonment_year": None,
                "length_km": properties.get("length_km"),
                "road_type": mapped_type,
                "confidence": mapped_confidence,
                "itinere_id": properties.get("id"),
            }

            roads.append(road)

        print(f"  Transformed: {len(roads)} roads")
        return roads
