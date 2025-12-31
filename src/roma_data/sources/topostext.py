"""
ToposText Ancient Places data source.

Downloads and processes ancient place data from ToposText.org.
ToposText links ancient texts to geographic locations, providing
rich citations from classical literature.

References:
    - ToposText: https://topostext.org
    - Downloads: https://topostext.org/TT-downloads
    - Brady Kiesling, Aikaterini Laskaridis Foundation
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests

from roma_data.constants import TOPOSTEXT_PLACES_URL
from roma_data.sources.base import DataSource

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


class ToposTextSource(DataSource):
    """Data source for ToposText ancient text citations."""

    name = "topostext"
    description = "ToposText Ancient Place Citations"

    def __init__(self, config: "Config") -> None:
        super().__init__(config)
        self.places_file = self.raw_dir / "topostext_places.geojson"

    def download(self) -> int:
        """
        Download ToposText places GeoJSON.

        Returns:
            Number of places downloaded.
        """
        self.ensure_dirs()

        # Check cache
        if self.config.cache_downloads and self.places_file.exists():
            logger.info(f"Using cached ToposText data: {self.places_file}")
            with open(self.places_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data.get("features", []))
            print(f"  Using cached: {count} ToposText places")
            return count

        print("  Downloading ToposText places...")
        try:
            response = requests.get(TOPOSTEXT_PLACES_URL, timeout=60)
            response.raise_for_status()

            data = response.json()
            with open(self.places_file, "w", encoding="utf-8") as f:
                json.dump(data, f)

            count = len(data.get("features", []))
            print(f"  Downloaded: {count} ToposText places")
            return count

        except requests.RequestException as e:
            logger.warning(f"ToposText download failed: {e}")
            print(f"  ToposText download failed: {e}")
            return 0
        except json.JSONDecodeError as e:
            logger.warning(f"ToposText JSON parse error: {e}")
            print(f"  ToposText JSON parse error: {e}")
            return 0

    def transform(self) -> List[Dict[str, Any]]:
        """
        Transform ToposText places to location records.

        ToposText provides places with ancient text citations,
        linking locations to classical literature.

        Returns:
            List of location records.
        """
        if not self.places_file.exists():
            return []

        with open(self.places_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        locations: List[Dict[str, Any]] = []
        features = data.get("features", [])

        for feature in features:
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            # Extract coordinates
            coords = geometry.get("coordinates", [])
            if geometry.get("type") != "Point" or len(coords) < 2:
                continue

            lon, lat = coords[0], coords[1]

            # Extract identifiers
            name = props.get("name", "")
            topostext_url = props.get("ToposText", "")
            topostext_id = self._extract_id(topostext_url)

            if not name or not topostext_id:
                continue

            # Extract Pleiades reference
            pleiades_uri = props.get("Pleiades", "")
            if pleiades_uri and not pleiades_uri.startswith("http"):
                pleiades_uri = None

            # Extract Wikidata ID
            wikidata = props.get("Wikidata", "")
            wikidata_id = wikidata if wikidata.startswith("Q") else None

            # Map ToposText type to our types
            tt_type = props.get("type", "").lower()
            location_type = self._map_type(tt_type)

            # Build description with citation count
            references = props.get("references", "")
            greek_name = props.get("Greek", "")
            description = props.get("description", "")

            if references:
                description = f"{description} [{references}]" if description else references

            location = {
                "id": f"topostext_{topostext_id}",
                "name_latin": name,
                "name_modern": props.get("modern place"),
                "name_greek": greek_name if greek_name else None,
                "type": location_type,
                "latitude": lat,
                "longitude": lon,
                "founding_year": None,
                "destruction_year": None,
                "peak_population": None,
                "province_id": None,
                "parent_location_id": None,
                "description": description,
                "thumbnail_filename": None,
                "confidence": self._map_confidence(props.get("confidence", "")),
                "pleiades_uri": pleiades_uri,
                "barrington_ref": None,
                "wikidata_id": wikidata_id,
                "region": props.get("region"),
                "country": props.get("country"),
                "topostext_url": topostext_url,
                "wikipedia_url": props.get("Wikipedia"),
            }

            locations.append(location)

        print(f"  Transformed: {len(locations)} ToposText locations")
        return locations

    def transform_citations(self) -> List[Dict[str, Any]]:
        """
        Extract citation counts from ToposText places.

        This provides the number of ancient text references
        for each location.

        Returns:
            List of citation records.
        """
        if not self.places_file.exists():
            return []

        with open(self.places_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        citations: List[Dict[str, Any]] = []
        features = data.get("features", [])

        for feature in features:
            props = feature.get("properties", {})
            topostext_url = props.get("ToposText", "")
            topostext_id = self._extract_id(topostext_url)

            if not topostext_id:
                continue

            references = props.get("references", "")
            if not references:
                continue

            # Parse "X in Y texts" format
            match = re.match(r"(\d+)\s+in\s+(\d+)\s+texts?", references)
            if match:
                ref_count = int(match.group(1))
                text_count = int(match.group(2))
            else:
                continue

            citation = {
                "location_id": f"topostext_{topostext_id}",
                "reference_count": ref_count,
                "text_count": text_count,
                "topostext_url": topostext_url,
            }

            citations.append(citation)

        print(f"  Transformed: {len(citations)} ToposText citations")
        return citations

    def _extract_id(self, url: str) -> Optional[str]:
        """Extract ToposText ID from URL."""
        if not url:
            return None
        # URL format: https://topostext.org/place/XXXXXX
        match = re.search(r"/place/(\w+)$", url)
        return match.group(1) if match else None

    def _map_type(self, tt_type: str) -> str:
        """Map ToposText type to standard location type."""
        type_map = {
            "polity": "city",
            "settlement": "settlement",
            "sanctuary": "temple",
            "temple": "temple",
            "necropolis": "cemetery",
            "theatre": "theater",
            "stadium": "stadium",
            "bridge": "bridge",
            "aqueduct": "aqueduct",
            "fort": "fort",
            "fortress": "fort",
            "mine": "mine",
            "quarry": "quarry",
            "harbor": "port",
            "port": "port",
            "island": "island",
            "mountain": "mountain",
            "river": "river",
            "lake": "lake",
            "spring": "spring",
            "road": "road",
            "villa": "villa",
            "palace": "palace",
            "bath": "bath",
            "region": "region",
        }
        return type_map.get(tt_type, "other")

    def _map_confidence(self, confidence: str) -> str:
        """Map ToposText confidence to standard values."""
        conf_lower = confidence.lower() if confidence else ""
        if "certain" in conf_lower:
            return "certain"
        elif "probable" in conf_lower:
            return "probable"
        elif "possible" in conf_lower:
            return "possible"
        elif "rough" in conf_lower or "approximate" in conf_lower:
            return "approximate"
        return "probable"
