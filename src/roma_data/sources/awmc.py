"""
AWMC Province Boundaries data source.

Downloads and processes province boundary GeoJSON from the Ancient World Mapping Center.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

import requests

from roma_data.constants import AWMC_PROVINCE_URLS, PROVINCE_COLORS
from roma_data.sources.base import DataSource

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)

# Province era ranges for temporal data
PROVINCE_ERA_RANGES: dict[str, dict[str, Any]] = {
    "roman_empire_bce_60": {
        "name": "Republican Era",
        "start_year": -200,
        "end_year": -27,
    },
    "roman_empire_ce_117": {
        "name": "Trajanic Peak",
        "start_year": 98,
        "end_year": 117,
    },
    "roman_empire_ce_200": {
        "name": "Severan Era",
        "start_year": 193,
        "end_year": 235,
    },
    "roman_empire_post_diocletian": {
        "name": "Diocletian Era",
        "start_year": 284,
        "end_year": 395,
    },
}


class AWMCSource(DataSource):
    """Data source for AWMC province boundaries."""

    name = "awmc"
    description = "Ancient World Mapping Center Province Boundaries"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.awmc_dir = self.raw_dir / "awmc"

    def download(self) -> int:
        """
        Download AWMC GeoJSON files.

        Returns:
            Number of files downloaded.
        """
        self.ensure_dirs()
        self.awmc_dir.mkdir(parents=True, exist_ok=True)

        downloaded = 0

        for era_name, url in AWMC_PROVINCE_URLS.items():
            dest_path = self.awmc_dir / f"awmc_{era_name}.geojson"

            # Check cache
            if self.config.cache_downloads and dest_path.exists():
                logger.info(f"Using cached AWMC data: {dest_path.name}")
                downloaded += 1
                continue

            print(f"  Downloading {era_name}...")
            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()

                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(response.text)

                downloaded += 1
                logger.info(f"Downloaded AWMC {era_name}")

            except requests.RequestException as e:
                logger.warning(f"Failed to download {era_name}: {e}")

        print(f"  Downloaded: {downloaded} AWMC province files")
        return downloaded

    def transform(self) -> list[dict[str, Any]]:
        """
        Transform AWMC province boundaries to processed format.

        Returns:
            List of province records.
        """
        provinces: list[dict[str, Any]] = []
        color_index = 0
        name_counter: dict[str, int] = {}

        for era_name, era_info in PROVINCE_ERA_RANGES.items():
            geojson_path = self.awmc_dir / f"awmc_{era_name}.geojson"

            if not geojson_path.exists():
                logger.debug(f"AWMC file not found: {geojson_path}")
                continue

            print(f"  Processing: {era_name}")

            with open(geojson_path, encoding="utf-8") as f:
                geojson = json.load(f)

            features = geojson.get("features", [])

            for i, feature in enumerate(features):
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})

                if geometry.get("type") not in ("Polygon", "MultiPolygon"):
                    continue

                # Calculate centroid
                coords = geometry.get("coordinates", [])
                centroid = self._calculate_centroid(coords, geometry["type"])

                # Generate province name
                latin_name = properties.get("name") or f"{era_info['name']} Region {i+1}"
                latin_name = re.sub(r'\s*\([^)]*\)\s*$', '', latin_name).strip()

                # Handle duplicate names by adding era suffix
                if latin_name in name_counter:
                    name_counter[latin_name] += 1
                    unique_name = f"{latin_name} ({era_info['name']})"
                else:
                    name_counter[latin_name] = 1
                    unique_name = latin_name

                # Generate ID
                province_id = f"awmc_{era_name}_{i}"

                # Serialize geometry to GeoJSON string
                polygon_geojson = json.dumps(geometry)

                province = {
                    "id": province_id,
                    "name": unique_name,
                    "name_latin": latin_name,
                    "start_year": era_info["start_year"],
                    "end_year": era_info["end_year"],
                    "polygon_geojson": polygon_geojson,
                    "centroid_lat": centroid[1] if centroid else None,
                    "centroid_lon": centroid[0] if centroid else None,
                    "parent_entity": era_info["name"],
                    "color_hex": PROVINCE_COLORS[color_index % len(PROVINCE_COLORS)],
                }

                provinces.append(province)
                color_index += 1

        print(f"  Transformed: {len(provinces)} provinces")
        return provinces

    def _calculate_centroid(
        self,
        coords: list[Any],
        geom_type: str,
    ) -> tuple[float, float] | None:
        """Calculate the centroid of a polygon or multipolygon."""
        all_points: list[tuple[float, float]] = []

        if geom_type == "Polygon":
            # Polygon: [ring1, ring2, ...] where each ring is [[lon, lat], ...]
            if coords and len(coords) > 0:
                outer_ring = coords[0]
                for point in outer_ring:
                    if len(point) >= 2:
                        all_points.append((point[0], point[1]))

        elif geom_type == "MultiPolygon":
            # MultiPolygon: [polygon1, polygon2, ...] where each is like Polygon
            for polygon in coords:
                if polygon and len(polygon) > 0:
                    outer_ring = polygon[0]
                    for point in outer_ring:
                        if len(point) >= 2:
                            all_points.append((point[0], point[1]))

        if not all_points:
            return None

        # Simple centroid: average of all points
        avg_lon = sum(p[0] for p in all_points) / len(all_points)
        avg_lat = sum(p[1] for p in all_points) / len(all_points)

        return (avg_lon, avg_lat)
