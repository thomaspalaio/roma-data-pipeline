"""
SQLite database export for Roma Data Pipeline.

Creates a SQLite database with FTS5 search indexes from processed data.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from roma_data.constants import (
    CREATE_TABLES_SQL,
    DEFAULT_TIMELINE_MARKERS,
)

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)


class SQLiteExporter:
    """Exports processed data to SQLite database."""

    def __init__(self, config: "Config") -> None:
        self.config = config
        self.processed_dir = config.output_dir / "processed"

    def export(self, output_path: Path | None = None) -> Path:
        """
        Build complete SQLite database from processed JSON files.

        Args:
            output_path: Optional custom output path. Defaults to config.output_path.

        Returns:
            Path to the created database file.
        """
        db_path = output_path or self.config.output_path
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing database
        if db_path.exists():
            db_path.unlink()
            logger.info(f"Removed existing database: {db_path}")

        conn = self._create_database(db_path)

        try:
            counts = {
                "locations": self._insert_locations(conn),
                "provinces": self._insert_provinces(conn),
                "roads": self._insert_roads(conn),
                "people": self._insert_people(conn),
                "events": self._insert_events(conn),
                "event_participants": self._insert_event_participants(conn),
                "road_cities": self._insert_road_cities(conn),
                "person_relationships": self._insert_person_relationships(conn),
                "person_roles": self._insert_person_roles(conn),
                "travel_network": self._insert_travel_network(conn),
                "ancient_sources": self._insert_ancient_sources(conn),
                "timeline_markers": self._insert_timeline_markers(conn),
            }

            self._rebuild_fts_indexes(conn)
            self._add_grdb_migrations(conn)
            self._optimize_database(conn)

            # Print summary
            print("\n=== Database Build Summary ===")
            total = 0
            for table, count in counts.items():
                if count > 0:
                    print(f"  {table}: {count}")
                    total += count

            file_size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"  Total records: {total}")
            print(f"  File size: {file_size_mb:.2f} MB")
            print(f"  Output: {db_path}")

            return db_path

        finally:
            conn.close()

    def _create_database(self, db_path: Path) -> sqlite3.Connection:
        """Create the SQLite database with schema."""
        print("\n=== Creating Database ===")

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        print("  Creating tables...")
        conn.executescript(CREATE_TABLES_SQL)

        conn.commit()
        logger.info(f"Created database: {db_path}")

        return conn

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from processed directory."""
        path = self.processed_dir / filename
        if not path.exists():
            logger.debug(f"File not found: {path}")
            return []

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _insert_locations(self, conn: sqlite3.Connection) -> int:
        """Insert locations into database."""
        locations = self._load_json("locations.json")
        if not locations:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for loc in locations:
            try:
                cursor.execute(
                    """
                    INSERT INTO locations (
                        id, name_latin, name_modern, type, latitude, longitude,
                        founding_year, destruction_year, peak_population, province_id,
                        parent_location_id, description, thumbnail_filename, confidence,
                        pleiades_uri, wikidata_id, ancient_text_refs,
                        ancient_text_count, topostext_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        loc["id"],
                        loc["name_latin"],
                        loc.get("name_modern"),
                        loc["type"],
                        loc["latitude"],
                        loc["longitude"],
                        loc.get("founding_year"),
                        loc.get("destruction_year"),
                        loc.get("peak_population"),
                        loc.get("province_id"),
                        loc.get("parent_location_id"),
                        loc.get("description"),
                        loc.get("thumbnail_filename"),
                        loc.get("confidence", "probable"),
                        loc.get("pleiades_uri"),
                        loc.get("wikidata_id"),
                        loc.get("ancient_text_refs"),
                        loc.get("ancient_text_count"),
                        loc.get("topostext_url"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError as e:
                logger.debug(f"Duplicate location: {loc['id']} - {e}")

        conn.commit()
        print(f"  Inserted: {inserted} locations")
        return inserted

    def _insert_provinces(self, conn: sqlite3.Connection) -> int:
        """Insert provinces into database."""
        provinces = self._load_json("provinces.json")
        if not provinces:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for prov in provinces:
            try:
                cursor.execute(
                    """
                    INSERT INTO provinces (
                        id, name, name_latin, start_year, end_year,
                        polygon_geojson, centroid_lat, centroid_lon,
                        parent_entity, color_hex
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        prov["id"],
                        prov["name"],
                        prov["name_latin"],
                        prov["start_year"],
                        prov.get("end_year"),
                        prov["polygon_geojson"],
                        prov.get("centroid_lat"),
                        prov.get("centroid_lon"),
                        prov.get("parent_entity"),
                        prov.get("color_hex"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError as e:
                logger.debug(f"Duplicate province: {prov['id']} - {e}")

        conn.commit()
        print(f"  Inserted: {inserted} provinces")
        return inserted

    def _insert_roads(self, conn: sqlite3.Connection) -> int:
        """Insert roads into database."""
        roads = self._load_json("roads.json")
        if not roads:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for road in roads:
            try:
                cursor.execute(
                    """
                    INSERT INTO roads (
                        id, name, name_latin, path_geojson, construction_year,
                        abandonment_year, length_km, road_type, confidence, itinere_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        road["id"],
                        road.get("name"),
                        road.get("name_latin"),
                        road["path_geojson"],
                        road.get("construction_year"),
                        road.get("abandonment_year"),
                        road.get("length_km"),
                        road.get("road_type", "secondary"),
                        road.get("confidence", "probable"),
                        road.get("itinere_id"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError as e:
                logger.debug(f"Duplicate road: {road['id']} - {e}")

        conn.commit()
        print(f"  Inserted: {inserted} roads")
        return inserted

    def _insert_people(self, conn: sqlite3.Connection) -> int:
        """Insert people into database."""
        people = self._load_json("people.json")
        if not people:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for person in people:
            try:
                cursor.execute(
                    """
                    INSERT INTO people (
                        id, name, name_latin, birth_year, death_year,
                        birth_location_id, death_location_id,
                        role, description, wikidata_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        person["id"],
                        person["name"],
                        person.get("name_latin"),
                        person.get("birth_year"),
                        person.get("death_year"),
                        person.get("birth_location_id"),
                        person.get("death_location_id"),
                        person.get("role"),
                        person.get("description"),
                        person.get("wikidata_id"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError as e:
                logger.debug(f"Duplicate person: {person['id']} - {e}")

        conn.commit()
        print(f"  Inserted: {inserted} people")
        return inserted

    def _insert_events(self, conn: sqlite3.Connection) -> int:
        """Insert events into database."""
        events = self._load_json("events.json")
        if not events:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for event in events:
            try:
                cursor.execute(
                    """
                    INSERT INTO events (
                        id, name, year, end_year, type, location_id,
                        description, outcome, significance, wikidata_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event["id"],
                        event["name"],
                        event["year"],
                        event.get("end_year"),
                        event["type"],
                        event.get("location_id"),
                        event.get("description"),
                        event.get("outcome"),
                        event.get("significance"),
                        event.get("wikidata_id"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError as e:
                logger.debug(f"Duplicate event: {event['id']} - {e}")

        conn.commit()
        print(f"  Inserted: {inserted} events")
        return inserted

    def _insert_event_participants(self, conn: sqlite3.Connection) -> int:
        """Insert event participants into database."""
        participants = self._load_json("event_participants.json")
        if not participants:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for p in participants:
            try:
                cursor.execute(
                    """
                    INSERT INTO event_participants (
                        id, event_id, person_id, role, side
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        p["id"],
                        p["event_id"],
                        p["person_id"],
                        p.get("role", "participant"),
                        p.get("side"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        if inserted:
            print(f"  Inserted: {inserted} event participants")
        return inserted

    def _insert_road_cities(self, conn: sqlite3.Connection) -> int:
        """Insert road cities into database."""
        road_cities = self._load_json("road_cities.json")
        if not road_cities:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for rc in road_cities:
            try:
                cursor.execute(
                    """
                    INSERT INTO road_cities (
                        id, road_id, location_id, sequence_order, distance_from_start_km
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rc["id"],
                        rc["road_id"],
                        rc["location_id"],
                        rc.get("sequence_order"),
                        rc.get("distance_from_start_km"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        if inserted:
            print(f"  Inserted: {inserted} road cities")
        return inserted

    def _insert_person_relationships(self, conn: sqlite3.Connection) -> int:
        """Insert person relationships into database."""
        relationships = self._load_json("person_relationships.json")
        if not relationships:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for rel in relationships:
            try:
                cursor.execute(
                    """
                    INSERT INTO person_relationships (
                        id, person1_id, person2_id, relationship_type,
                        start_year, end_year
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rel["id"],
                        rel["person1_id"],
                        rel["person2_id"],
                        rel["relationship_type"],
                        rel.get("start_year"),
                        rel.get("end_year"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        if inserted:
            print(f"  Inserted: {inserted} person relationships")
        return inserted

    def _insert_person_roles(self, conn: sqlite3.Connection) -> int:
        """Insert person roles into database."""
        roles = self._load_json("person_roles.json")
        if not roles:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for role in roles:
            try:
                cursor.execute(
                    """
                    INSERT INTO person_roles (
                        id, person_id, role, start_year, end_year, location_id
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        role["id"],
                        role["person_id"],
                        role["role"],
                        role.get("start_year"),
                        role.get("end_year"),
                        role.get("location_id"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        if inserted:
            print(f"  Inserted: {inserted} person roles")
        return inserted

    def _insert_travel_network(self, conn: sqlite3.Connection) -> int:
        """Insert travel network edges into database."""
        network = self._load_json("travel_network.json")
        if not network:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for edge in network:
            try:
                cursor.execute(
                    """
                    INSERT INTO travel_network (
                        id, source_location_id, target_location_id,
                        source_name, target_name, distance_km,
                        travel_days_foot, travel_days_horse, travel_days_cart, travel_days_ship,
                        cost_denarii_per_kg, seasonal, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        edge["id"],
                        edge["source_location_id"],
                        edge["target_location_id"],
                        edge.get("source_name"),
                        edge.get("target_name"),
                        edge.get("distance_km", 0),
                        edge.get("travel_days_foot"),
                        edge.get("travel_days_horse"),
                        edge.get("travel_days_cart"),
                        edge.get("travel_days_ship"),
                        edge.get("cost_denarii_per_kg"),
                        1 if edge.get("seasonal") else 0,
                        edge.get("data_source", "orbis"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        if inserted:
            print(f"  Inserted: {inserted} travel network routes")
        return inserted

    def _insert_ancient_sources(self, conn: sqlite3.Connection) -> int:
        """Insert ancient sources into database."""
        sources = self._load_json("ancient_sources.json")
        if not sources:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for source in sources:
            try:
                cursor.execute(
                    """
                    INSERT INTO ancient_sources (
                        id, location_id, location_name, topostext_url,
                        reference_count, text_count, name_greek, description, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source["id"],
                        source.get("location_id"),
                        source.get("location_name"),
                        source.get("topostext_url"),
                        source.get("reference_count", 0),
                        source.get("text_count", 0),
                        source.get("name_greek"),
                        source.get("description"),
                        source.get("data_source", "topostext"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        if inserted:
            print(f"  Inserted: {inserted} ancient sources")
        return inserted

    def _insert_timeline_markers(self, conn: sqlite3.Connection) -> int:
        """Insert default timeline markers."""
        cursor = conn.cursor()
        inserted = 0

        for year, name, description, marker_type in DEFAULT_TIMELINE_MARKERS:
            try:
                cursor.execute(
                    """
                    INSERT INTO timeline_markers (year, name, description, marker_type)
                    VALUES (?, ?, ?, ?)
                    """,
                    (year, name, description, marker_type),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        print(f"  Inserted: {inserted} timeline markers")
        return inserted

    def _rebuild_fts_indexes(self, conn: sqlite3.Connection) -> None:
        """Rebuild FTS indexes for all data."""
        print("  Building FTS search indexes...")

        cursor = conn.cursor()

        # Populate location search index
        cursor.execute(
            """
            INSERT INTO location_search(location_id, name_latin, name_modern, description)
            SELECT id, name_latin, COALESCE(name_modern, ''), COALESCE(description, '')
            FROM locations
            """
        )

        # Populate people search index
        cursor.execute(
            """
            INSERT INTO people_search(person_id, name, name_latin, description)
            SELECT id, name, COALESCE(name_latin, ''), COALESCE(description, '')
            FROM people
            """
        )

        conn.commit()

    def _add_grdb_migrations(self, conn: sqlite3.Connection) -> None:
        """Add GRDB migration tracking table for iOS compatibility."""
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grdb_migrations (
                identifier TEXT NOT NULL PRIMARY KEY
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO grdb_migrations (identifier) VALUES ('v1_initial')
        """)

        conn.commit()

    def _optimize_database(self, conn: sqlite3.Connection) -> None:
        """Optimize the database for read performance."""
        print("  Optimizing database...")

        conn.execute("ANALYZE")

        # Switch to DELETE journal mode before VACUUM (WAL doesn't support VACUUM well)
        conn.execute("PRAGMA journal_mode = DELETE")
        conn.execute("VACUUM")


def export_to_sqlite(config: "Config", output_path: Path | None = None) -> Path:
    """
    Convenience function to export data to SQLite.

    Args:
        config: Pipeline configuration.
        output_path: Optional output path.

    Returns:
        Path to the created database.
    """
    exporter = SQLiteExporter(config)
    return exporter.export(output_path)
