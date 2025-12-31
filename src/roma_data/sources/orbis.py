"""
ORBIS Travel Network data source.

Downloads and processes travel network data from the ORBIS project (Stanford).
Data sourced from sfsheath/gorbit GitHub repository.

References:
    - ORBIS: https://orbis.stanford.edu
    - Data: https://github.com/sfsheath/gorbit
    - Scheidel, W. and Meeks, E. (2012). ORBIS: The Stanford Geospatial
      Network Model of the Roman World.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests

from roma_data.constants import ORBIS_SITES_URL, ORBIS_EDGES_URL, TRAVEL_SPEEDS
from roma_data.sources.base import DataSource

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


class ORBISSource(DataSource):
    """Data source for ORBIS travel network."""

    name = "orbis"
    description = "ORBIS Stanford Travel Network Model"

    def __init__(self, config: "Config") -> None:
        super().__init__(config)
        self.sites_file = self.raw_dir / "orbis_sites.csv"
        self.edges_file = self.raw_dir / "orbis_edges.csv"

    def download(self) -> int:
        """
        Download ORBIS site and edge data from GitHub.

        Returns:
            Number of records downloaded.
        """
        self.ensure_dirs()

        total = 0

        # Download sites CSV
        if self.config.cache_downloads and self.sites_file.exists():
            logger.info(f"Using cached: {self.sites_file.name}")
            with open(self.sites_file, "r", encoding="utf-8") as f:
                total += sum(1 for _ in f) - 1  # Subtract header
        else:
            print("  Downloading ORBIS sites...")
            try:
                response = requests.get(ORBIS_SITES_URL, timeout=30)
                response.raise_for_status()
                with open(self.sites_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                total += response.text.count("\n") - 1
                print(f"  Downloaded {total} ORBIS sites")
            except requests.RequestException as e:
                logger.warning(f"ORBIS sites download failed: {e}")
                print(f"  ORBIS sites download failed: {e}")

        # Download edges CSV
        if self.config.cache_downloads and self.edges_file.exists():
            logger.info(f"Using cached: {self.edges_file.name}")
            with open(self.edges_file, "r", encoding="utf-8") as f:
                edges_count = sum(1 for _ in f) - 1
                total += edges_count
        else:
            print("  Downloading ORBIS edges...")
            try:
                response = requests.get(ORBIS_EDGES_URL, timeout=30)
                response.raise_for_status()
                with open(self.edges_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                edges_count = response.text.count("\n") - 1
                total += edges_count
                print(f"  Downloaded {edges_count} ORBIS edges")
            except requests.RequestException as e:
                logger.warning(f"ORBIS edges download failed: {e}")
                print(f"  ORBIS edges download failed: {e}")

        print(f"  Downloaded: {total} ORBIS records")
        return total

    def transform(self) -> List[Dict[str, Any]]:
        """
        Transform ORBIS sites to location records.

        Returns:
            List of location records from ORBIS sites.
        """
        if not self.sites_file.exists():
            return []

        locations: List[Dict[str, Any]] = []
        site_names: Dict[int, str] = {}  # Store for edge lookup

        with open(self.sites_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                site_id = row.get("id", "").strip('"')
                name = row.get("title", "").strip('"')
                lat = row.get("latitude", "").strip('"')
                lon = row.get("longitude", "").strip('"')
                pleiades_id = row.get("pleiades", "").strip('"')

                if not all([site_id, name, lat, lon]):
                    continue

                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    site_id_int = int(site_id)
                except ValueError:
                    continue

                site_names[site_id_int] = name

                # Construct Pleiades URI if available
                pleiades_uri = None
                if pleiades_id:
                    pleiades_uri = f"https://pleiades.stoa.org/places/{pleiades_id}"

                location = {
                    "id": f"orbis_{site_id}",
                    "name_latin": name,
                    "name_modern": None,
                    "type": "city",
                    "latitude": lat_f,
                    "longitude": lon_f,
                    "founding_year": None,
                    "destruction_year": None,
                    "peak_population": None,
                    "province_id": None,
                    "parent_location_id": None,
                    "description": f"ORBIS network node: {name}",
                    "thumbnail_filename": None,
                    "confidence": "certain",
                    "pleiades_uri": pleiades_uri,
                    "barrington_ref": None,
                    "wikidata_id": None,
                }

                locations.append(location)

        # Store site names for edge transform
        self._site_names = site_names

        print(f"  Transformed: {len(locations)} ORBIS locations")
        return locations

    def transform_travel_network(self) -> List[Dict[str, Any]]:
        """
        Transform ORBIS edges to travel network records.

        Returns:
            List of travel network edge records.
        """
        if not self.edges_file.exists():
            return []

        # Load site names if not already loaded
        if not hasattr(self, "_site_names"):
            self.transform()  # This populates _site_names

        edges: List[Dict[str, Any]] = []

        with open(self.edges_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                source_id = row.get("source", "").strip('"')
                target_id = row.get("target", "").strip('"')
                distance_km = row.get("km", "").strip('"')
                days = row.get("days", "").strip('"')
                expense = row.get("expense", "").strip('"')
                route_type = row.get("type", "road").strip('"')

                if not all([source_id, target_id]):
                    continue

                try:
                    source_int = int(source_id)
                    target_int = int(target_id)
                    distance = float(distance_km) if distance_km else 0
                    travel_days = float(days) if days else None
                    cost = float(expense) if expense else None
                except ValueError:
                    continue

                # Get site names
                source_name = self._site_names.get(source_int, f"Site {source_id}")
                target_name = self._site_names.get(target_int, f"Site {target_id}")

                # Calculate travel times for different modes
                if distance > 0:
                    travel_days_foot = distance / TRAVEL_SPEEDS["foot"]
                    travel_days_horse = distance / TRAVEL_SPEEDS["horse"]
                    travel_days_cart = distance / TRAVEL_SPEEDS["cart"]
                else:
                    travel_days_foot = travel_days
                    travel_days_horse = travel_days
                    travel_days_cart = travel_days

                # Sea routes get ship travel time
                travel_days_ship = None
                if route_type in ("sea", "river", "coastal"):
                    travel_days_ship = travel_days

                edge = {
                    "id": f"orbis_edge_{i}",
                    "source_location_id": f"orbis_{source_id}",
                    "target_location_id": f"orbis_{target_id}",
                    "source_name": source_name,
                    "target_name": target_name,
                    "distance_km": distance,
                    "travel_days_foot": travel_days_foot,
                    "travel_days_horse": travel_days_horse,
                    "travel_days_cart": travel_days_cart,
                    "travel_days_ship": travel_days_ship,
                    "cost_denarii_per_kg": cost,
                    "route_type": route_type,
                    "seasonal": route_type == "sea",
                    "data_source": "orbis",
                }

                edges.append(edge)

        print(f"  Transformed: {len(edges)} travel network edges")
        return edges
