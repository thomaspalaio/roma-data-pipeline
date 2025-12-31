"""
Pleiades data source - Ancient places gazetteer.

Downloads and processes location data from Pleiades (pleiades.stoa.org).
"""

from __future__ import annotations

import gzip
import json
import logging
import re
import shutil
from typing import TYPE_CHECKING, Any

import requests
from tqdm import tqdm

from roma_data.constants import (
    CONFIDENCE_MAP,
    LOCATION_TYPE_MAP,
    PERIOD_TO_YEARS,
    PLEIADES_JSON_URL,
    ROMAN_END_YEAR,
    ROMAN_START_YEAR,
    ROMAN_TIME_PERIODS,
)
from roma_data.sources.base import DataSource

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


class PleiadesSource(DataSource):
    """Data source for Pleiades ancient place gazetteer."""

    name = "pleiades"
    description = "Pleiades Gazetteer of Ancient Places"

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def download(self) -> int:
        """
        Download Pleiades JSON dump.

        Returns:
            Number of places downloaded.
        """
        self.ensure_dirs()
        gz_path = self.raw_dir / "pleiades-places-latest.json.gz"
        output_path = self.raw_dir / "pleiades-places.json"

        # Check cache
        if self.config.cache_downloads and output_path.exists():
            logger.info(f"Using cached Pleiades data: {output_path}")
            with open(output_path, encoding="utf-8") as f:
                data = json.load(f)
            places = data.get("@graph", data) if isinstance(data, dict) else data
            return len(places)

        logger.info(f"Downloading Pleiades from {PLEIADES_JSON_URL}")
        print("  Downloading Pleiades JSON dump...")

        # Download with progress bar
        response = requests.get(PLEIADES_JSON_URL, stream=True, timeout=120)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(gz_path, "wb") as f:
            with tqdm(total=total_size, unit="B", unit_scale=True, desc="Pleiades") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

        # Decompress
        print("  Extracting...")
        with gzip.open(gz_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Clean up compressed file
        gz_path.unlink()

        # Count places
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        places = data.get("@graph", data) if isinstance(data, dict) else data
        logger.info(f"Downloaded {len(places)} places from Pleiades")
        print(f"  Downloaded: {len(places)} places")

        return len(places)

    def transform(self) -> list[dict[str, Any]]:
        """
        Transform Pleiades data to processed format.

        Returns:
            List of transformed location records.
        """
        input_path = self.raw_dir / "pleiades-places.json"

        if not input_path.exists():
            raise FileNotFoundError(f"Pleiades data not found: {input_path}. Run download first.")

        print("  Loading Pleiades JSON...")
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)

        places = data.get("@graph", data) if isinstance(data, dict) else data
        print(f"  Total places in Pleiades: {len(places)}")

        transformed = []
        skipped_no_coords = 0
        skipped_not_roman = 0

        for place in tqdm(places, desc="Transforming", disable=not self.config.verbose):
            if not isinstance(place, dict):
                continue

            # Must have coordinates
            if not self._has_valid_coordinates(place):
                skipped_no_coords += 1
                continue

            # Must be Roman period (unless filtering disabled)
            if not self._is_roman_period(place):
                skipped_not_roman += 1
                continue

            # Extract coordinates
            repr_point = place.get("reprPoint")
            lon, lat = repr_point[0], repr_point[1]

            # Apply bbox filter if configured
            if self.config.bbox:
                min_lon, min_lat, max_lon, max_lat = self.config.bbox
                if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                    continue

            # Extract dates
            founding_year, destruction_year = self._extract_temporal_bounds(place)

            # Apply time filter if configured
            if self.config.time_range:
                start, end = self.config.time_range
                if founding_year is not None and founding_year > end:
                    continue
                if destruction_year is not None and destruction_year < start:
                    continue

            # Map place type
            mapped_type = self._map_place_type(place)

            # Apply type filter if configured
            if self.config.location_types and mapped_type not in self.config.location_types:
                continue

            # Get names
            name_latin = self._get_best_latin_name(place)
            name_modern = self._get_modern_name(place)

            # Get confidence
            confidence = self._map_confidence(place)

            # Extract Pleiades ID
            pleiades_id = place.get("id", "").split("/")[-1]

            # Build record
            record = {
                "id": f"pleiades_{pleiades_id}",
                "name_latin": name_latin,
                "name_modern": name_modern,
                "type": mapped_type,
                "latitude": lat,
                "longitude": lon,
                "founding_year": founding_year,
                "destruction_year": destruction_year,
                "peak_population": None,
                "province_id": None,
                "parent_location_id": None,
                "description": place.get("description", ""),
                "thumbnail_filename": None,
                "confidence": confidence,
                "pleiades_uri": place.get("uri") or f"https://pleiades.stoa.org/places/{pleiades_id}",
                "barrington_ref": self._extract_barrington_ref(place),
                "wikidata_id": None,
            }

            transformed.append(record)

        print(f"  Filtered: {len(transformed)} Roman locations")
        print(f"  Skipped (no coordinates): {skipped_no_coords}")
        print(f"  Skipped (not Roman period): {skipped_not_roman}")

        return transformed

    def _has_valid_coordinates(self, place: dict[str, Any]) -> bool:
        """Check if a place has valid coordinates."""
        repr_point = place.get("reprPoint")
        if repr_point and len(repr_point) >= 2:
            lon, lat = repr_point[0], repr_point[1]
            if lon is not None and lat is not None:
                if -180 <= lon <= 180 and -90 <= lat <= 90:
                    return True
        return False

    def _is_roman_period(self, place: dict[str, Any]) -> bool:
        """Check if a place existed during the Roman period."""
        # Check attestations in locations
        locations = place.get("locations", []) or []
        for loc in locations:
            if not isinstance(loc, dict):
                continue
            attestations = loc.get("attestations", []) or []
            for att in attestations:
                if not isinstance(att, dict):
                    continue
                tp = att.get("timePeriod", "").lower()
                for roman_period in ROMAN_TIME_PERIODS:
                    if roman_period in tp:
                        return True

        # Check place-level time periods
        time_periods = place.get("timePeriods", []) or []
        for tp in time_periods:
            tp_id = tp.get("id", "") if isinstance(tp, dict) else str(tp)
            for roman_period in ROMAN_TIME_PERIODS:
                if roman_period in tp_id.lower():
                    return True

        # Check date range
        min_date = place.get("minDate")
        max_date = place.get("maxDate")

        if min_date is not None and max_date is not None:
            try:
                min_year = int(min_date)
                max_year = int(max_date)
                if min_year <= ROMAN_END_YEAR and max_year >= ROMAN_START_YEAR:
                    return True
            except (ValueError, TypeError):
                pass

        # Fallback: Include places with Roman-era placeTypes in Roman territories
        place_types = place.get("placeTypes", []) or []
        roman_place_types = {"urban", "settlement", "fort", "port", "temple", "villa"}
        if any(pt.lower() in roman_place_types for pt in place_types):
            repr_point = place.get("reprPoint")
            if repr_point and len(repr_point) >= 2:
                lon, lat = repr_point[0], repr_point[1]
                # Mediterranean basin bounds
                if -10 <= lon <= 45 and 25 <= lat <= 55:
                    return True

        return False

    def _extract_temporal_bounds(self, place: dict[str, Any]) -> tuple[int | None, int | None]:
        """Extract founding and destruction years from temporal attestations."""
        min_year: int | None = None
        max_year: int | None = None

        # Strategy 1: Use explicit minDate/maxDate
        min_date = place.get("minDate")
        max_date = place.get("maxDate")

        if min_date is not None:
            try:
                min_year = int(min_date)
            except (ValueError, TypeError):
                pass

        if max_date is not None:
            try:
                max_year = int(max_date)
            except (ValueError, TypeError):
                pass

        if min_year is not None and max_year is not None:
            return (min_year, max_year)

        # Strategy 2: Extract from time period attestations
        locations = place.get("locations", []) or []
        all_periods: list[str] = []

        for loc in locations:
            if not isinstance(loc, dict):
                continue
            attestations = loc.get("attestations", []) or []
            for att in attestations:
                if not isinstance(att, dict):
                    continue
                tp = att.get("timePeriod", "").lower()
                if tp:
                    all_periods.append(tp)

        # Map periods to years
        for period in all_periods:
            if period in PERIOD_TO_YEARS:
                start, end = PERIOD_TO_YEARS[period]
                if min_year is None or start < min_year:
                    min_year = start
                if max_year is None or end > max_year:
                    max_year = end

        return (min_year, max_year)

    def _get_best_latin_name(self, place: dict[str, Any]) -> str:
        """Extract the best Latin name from a Pleiades place."""
        names = place.get("names", []) or []

        for name in names:
            if not isinstance(name, dict):
                continue
            attested = name.get("attested", "")
            romanized = name.get("romanized", "")
            language = name.get("language", "")

            if language in ("la", "lat", "latin") and romanized:
                return romanized
            if language in ("la", "lat", "latin") and attested:
                return attested

        for name in names:
            if isinstance(name, dict) and name.get("romanized"):
                return name["romanized"]

        return place.get("title", "Unknown")

    def _get_modern_name(self, place: dict[str, Any]) -> str | None:
        """Extract the modern name from a Pleiades place."""
        names = place.get("names", []) or []

        for name in names:
            if not isinstance(name, dict):
                continue
            name_type = name.get("nameType", "")
            if name_type == "modern" or name.get("language") in ("en", "it", "fr", "de", "es"):
                return name.get("romanized") or name.get("attested")

        return None

    def _map_place_type(self, place: dict[str, Any]) -> str:
        """Map Pleiades place types to app location type."""
        place_types = place.get("placeTypes", []) or []

        for pt in place_types:
            pt_str = str(pt).lower() if pt else ""
            if pt_str in LOCATION_TYPE_MAP:
                return LOCATION_TYPE_MAP[pt_str]

        return LOCATION_TYPE_MAP.get("default", "other")

    def _map_confidence(self, place: dict[str, Any]) -> str:
        """Map Pleiades location precision to app confidence."""
        locations = place.get("locations", []) or []

        for loc in locations:
            if not isinstance(loc, dict):
                continue
            accuracy = loc.get("accuracy", "")
            if accuracy:
                acc_lower = accuracy.lower()
                if acc_lower in CONFIDENCE_MAP:
                    return CONFIDENCE_MAP[acc_lower]

        return CONFIDENCE_MAP.get("default", "probable")

    def _extract_barrington_ref(self, place: dict[str, Any]) -> str | None:
        """Extract Barrington Atlas reference from Pleiades references."""
        references = place.get("references", []) or []

        for ref in references:
            if not isinstance(ref, dict):
                continue
            citation = ref.get("citation", "") or ref.get("shortTitle", "")
            if not citation:
                continue

            citation_lower = citation.lower()
            if "barrington" in citation_lower or "batlas" in citation_lower:
                match = re.search(
                    r'(?:map\s*)?(\d{1,2})\s*([A-H])\s*([1-6])',
                    citation,
                    re.IGNORECASE
                )
                if match:
                    map_num = match.group(1)
                    col = match.group(2).upper()
                    row = match.group(3)
                    return f"Map {map_num} {col}{row}"

                return citation[:100]

        return None
