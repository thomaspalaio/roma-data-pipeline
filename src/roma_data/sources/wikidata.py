"""
Wikidata SPARQL data source.

Queries Wikidata for Roman emperors, people, battles, and events.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

try:
    from SPARQLWrapper import JSON as SPARQL_JSON
    from SPARQLWrapper import SPARQLWrapper
except ImportError:
    SPARQLWrapper = None
    SPARQL_JSON = None

from roma_data.constants import WIKIDATA_SPARQL_ENDPOINT
from roma_data.sources.base import DataSource

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)

# Basic emperor query
WIKIDATA_EMPEROR_QUERY = """
SELECT DISTINCT ?person ?personLabel ?birthYear ?deathYear ?description
WHERE {
  ?person wdt:P39 wd:Q842606 .  # Roman emperor
  OPTIONAL { ?person wdt:P569 ?birth . BIND(YEAR(?birth) AS ?birthYear) }
  OPTIONAL { ?person wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }
  OPTIONAL { ?person schema:description ?description . FILTER(LANG(?description) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,la" . }
}
ORDER BY ?birthYear
"""

# Basic battle query
WIKIDATA_BATTLE_QUERY = """
SELECT DISTINCT ?battle ?battleLabel ?year ?locationLabel ?description
WHERE {
  ?battle wdt:P31/wdt:P279* wd:Q178561 .  # instance of battle
  ?battle wdt:P710 ?participant .  # participant
  { ?participant wdt:P31 wd:Q6256 . ?participant wdt:P17 wd:Q17 . }  # Ancient Rome
  UNION
  { ?battle wdt:P17 wd:Q17 . }  # country: Ancient Rome

  OPTIONAL { ?battle wdt:P585 ?date . BIND(YEAR(?date) AS ?year) }
  OPTIONAL { ?battle wdt:P276 ?location . }
  OPTIONAL { ?battle schema:description ?description . FILTER(LANG(?description) = "en") }

  FILTER(!BOUND(?year) || (?year >= -800 && ?year <= 500))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,la" . }
}
ORDER BY ?year
LIMIT 500
"""


class WikidataSource(DataSource):
    """Data source for Wikidata (people, events)."""

    name = "wikidata"
    description = "Wikidata SPARQL queries for Roman data"

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.wikidata_dir = self.raw_dir

    def download(self) -> int:
        """
        Run SPARQL queries against Wikidata.

        Returns:
            Total number of results downloaded.
        """
        if SPARQLWrapper is None:
            print("  SPARQLWrapper not installed. Run: pip install SPARQLWrapper")
            return 0

        self.ensure_dirs()
        self.wikidata_dir.mkdir(parents=True, exist_ok=True)

        total = 0

        # Download emperors
        emperors_path = self.wikidata_dir / "wikidata_emperors.json"
        if self.config.cache_downloads and emperors_path.exists():
            logger.info(f"Using cached: {emperors_path.name}")
            with open(emperors_path, encoding="utf-8") as f:
                total += len(json.load(f))
        else:
            results = self._query_wikidata(WIKIDATA_EMPEROR_QUERY, "Roman Emperors")
            if results:
                with open(emperors_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                total += len(results)

        # Download battles
        battles_path = self.wikidata_dir / "wikidata_battles.json"
        if self.config.cache_downloads and battles_path.exists():
            logger.info(f"Using cached: {battles_path.name}")
            with open(battles_path, encoding="utf-8") as f:
                total += len(json.load(f))
        else:
            results = self._query_wikidata(WIKIDATA_BATTLE_QUERY, "Roman Battles")
            if results:
                with open(battles_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                total += len(results)

        print(f"  Downloaded: {total} Wikidata records")
        return total

    def _query_wikidata(self, query: str, name: str) -> list[dict] | None:
        """Execute a SPARQL query against Wikidata."""
        try:
            sparql = SPARQLWrapper(WIKIDATA_SPARQL_ENDPOINT)
            sparql.setQuery(query)
            sparql.setReturnFormat(SPARQL_JSON)
            sparql.addCustomHttpHeader("User-Agent", "RomaDataPipeline/1.0")

            print(f"  Querying Wikidata for {name}...")
            results = sparql.query().convert()

            bindings = results.get("results", {}).get("bindings", [])
            print(f"  Found {len(bindings)} results")

            return bindings

        except Exception as e:
            logger.warning(f"SPARQL query error: {e}")
            print(f"  SPARQL query error: {e}")
            return None

    def transform(self) -> list[dict[str, Any]]:
        """Transform is split into transform_people() and transform_events()."""
        return []

    def transform_people(self) -> list[dict[str, Any]]:
        """Transform Wikidata people results."""
        emperors_path = self.wikidata_dir / "wikidata_emperors.json"

        if not emperors_path.exists():
            return []

        with open(emperors_path, encoding="utf-8") as f:
            emperors = json.load(f)

        people: list[dict[str, Any]] = []
        seen_ids: set = set()

        for emp in emperors:
            wikidata_uri = emp.get("person", {}).get("value", "")
            wikidata_id = wikidata_uri.split("/")[-1] if wikidata_uri else None

            if not wikidata_id or wikidata_id in seen_ids:
                continue
            seen_ids.add(wikidata_id)

            name = emp.get("personLabel", {}).get("value", "Unknown")
            birth_year = emp.get("birthYear", {}).get("value")
            death_year = emp.get("deathYear", {}).get("value")
            description = emp.get("description", {}).get("value")

            person = {
                "id": f"wikidata_{wikidata_id}",
                "name": name,
                "name_latin": name,
                "birth_year": int(birth_year) if birth_year else None,
                "death_year": int(death_year) if death_year else None,
                "birth_location_id": None,
                "death_location_id": None,
                "role": "emperor",
                "description": description,
                "wikidata_id": wikidata_id,
            }

            people.append(person)

        print(f"  Transformed: {len(people)} people")
        return people

    def transform_events(self) -> list[dict[str, Any]]:
        """Transform Wikidata event results."""
        battles_path = self.wikidata_dir / "wikidata_battles.json"

        if not battles_path.exists():
            return []

        with open(battles_path, encoding="utf-8") as f:
            battles = json.load(f)

        events: list[dict[str, Any]] = []
        seen_ids: set = set()

        for battle in battles:
            wikidata_uri = battle.get("battle", {}).get("value", "")
            wikidata_id = wikidata_uri.split("/")[-1] if wikidata_uri else None

            if not wikidata_id or wikidata_id in seen_ids:
                continue
            seen_ids.add(wikidata_id)

            name = battle.get("battleLabel", {}).get("value", "Unknown Battle")
            year = battle.get("year", {}).get("value")
            description = battle.get("description", {}).get("value")

            if not year:
                continue

            event = {
                "id": f"wikidata_{wikidata_id}",
                "name": name,
                "year": int(year),
                "end_year": None,
                "type": "battle",
                "location_id": None,
                "description": description,
                "outcome": None,
                "significance": None,
                "wikidata_id": wikidata_id,
            }

            events.append(event)

        print(f"  Transformed: {len(events)} events")
        return events
