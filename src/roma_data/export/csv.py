"""
CSV export for Roma Data Pipeline.

Exports database tables to CSV format for spreadsheet analysis.
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from roma_data.config import Config


def export_csv(
    database: Path,
    table: str,
    output: Path,
    verbose: bool = False
) -> int:
    """
    Export a table to CSV.

    Args:
        database: Path to SQLite database
        table: Table name to export
        output: Output CSV file path
        verbose: Print verbose output

    Returns:
        Number of rows exported
    """
    if not database.exists():
        raise FileNotFoundError(f"Database not found: {database}")

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row

    exporters = {
        "locations": _export_locations,
        "provinces": _export_provinces,
        "roads": _export_roads,
        "people": _export_people,
        "events": _export_events,
        "travel_network": _export_travel_network,
        "timeline_markers": _export_timeline_markers,
    }

    if table not in exporters:
        raise ValueError(f"Unknown table: {table}. Valid: {', '.join(exporters.keys())}")

    try:
        count = exporters[table](conn, output, verbose)
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            if verbose:
                print(f"  Table {table} does not exist, skipping")
            count = 0
        else:
            raise

    conn.close()

    if verbose:
        print(f"Exported {count} rows to {output}")

    return count


def _export_locations(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export locations table to CSV."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name_latin, name_modern, type, latitude, longitude,
               description, founding_year, destruction_year, peak_population,
               province_id, parent_location_id, thumbnail_filename,
               confidence, pleiades_uri, wikidata_id,
               ancient_text_refs, ancient_text_count, topostext_url
        FROM locations
        ORDER BY id
    """)

    columns = [
        "id", "name_latin", "name_modern", "type", "latitude", "longitude",
        "description", "founding_year", "destruction_year", "peak_population",
        "province_id", "parent_location_id", "thumbnail_filename",
        "confidence", "pleiades_uri", "wikidata_id",
        "ancient_text_refs", "ancient_text_count", "topostext_url"
    ]

    return _write_csv(output, columns, cursor.fetchall())


def _export_provinces(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export provinces table to CSV (without geometry)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, name_latin, start_year, end_year,
               centroid_lat, centroid_lon, parent_entity, color_hex
        FROM provinces
        ORDER BY id
    """)

    columns = [
        "id", "name", "name_latin", "start_year", "end_year",
        "centroid_lat", "centroid_lon", "parent_entity", "color_hex"
    ]

    return _write_csv(output, columns, cursor.fetchall())


def _export_roads(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export roads table to CSV (without geometry)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, name_latin, construction_year, abandonment_year,
               length_km, road_type, confidence, itinere_id
        FROM roads
        ORDER BY id
    """)

    columns = [
        "id", "name", "name_latin", "construction_year", "abandonment_year",
        "length_km", "road_type", "confidence", "itinere_id"
    ]

    return _write_csv(output, columns, cursor.fetchall())


def _export_people(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export people table to CSV."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, name_latin, birth_year, death_year,
               birth_location_id, death_location_id, role, description, wikidata_id
        FROM people
        ORDER BY birth_year, name
    """)

    columns = [
        "id", "name", "name_latin", "birth_year", "death_year",
        "birth_location_id", "death_location_id", "role", "description", "wikidata_id"
    ]

    return _write_csv(output, columns, cursor.fetchall())


def _export_events(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export events table to CSV."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, year, end_year, type, location_id,
               description, outcome, significance, wikidata_id
        FROM events
        ORDER BY year, name
    """)

    columns = [
        "id", "name", "year", "end_year", "type", "location_id",
        "description", "outcome", "significance", "wikidata_id"
    ]

    return _write_csv(output, columns, cursor.fetchall())


def _export_travel_network(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export travel network edges to CSV."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, source_location_id, target_location_id,
               source_name, target_name, distance_km,
               travel_days_foot, travel_days_horse,
               travel_days_cart, travel_days_ship, cost_denarii_per_kg,
               seasonal, data_source
        FROM travel_network
        ORDER BY source_location_id, target_location_id
    """)

    columns = [
        "id", "source_location_id", "target_location_id",
        "source_name", "target_name", "distance_km",
        "travel_days_foot", "travel_days_horse",
        "travel_days_cart", "travel_days_ship", "cost_denarii_per_kg",
        "seasonal", "data_source"
    ]

    return _write_csv(output, columns, cursor.fetchall())


def _export_timeline_markers(conn: sqlite3.Connection, output: Path, verbose: bool) -> int:
    """Export timeline markers to CSV."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, year, name, description, marker_type
        FROM timeline_markers
        ORDER BY year
    """)

    columns = ["id", "year", "name", "description", "marker_type"]

    return _write_csv(output, columns, cursor.fetchall())


def _write_csv(output: Path, columns: List[str], rows: List[Any]) -> int:
    """Write rows to CSV file."""
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)

    return len(rows)


def export_all_csv(config: "Config") -> None:
    """
    Export all tables to CSV files.

    Args:
        config: Pipeline configuration
    """
    output_dir = config.output_dir / "csv"
    output_dir.mkdir(parents=True, exist_ok=True)

    database = config.output_path

    tables = [
        "locations", "provinces", "roads", "people", "events",
        "travel_network", "timeline_markers"
    ]

    for table in tables:
        output_path = output_dir / f"{table}.csv"
        try:
            count = export_csv(database, table, output_path, config.verbose)
            if count > 0:
                print(f"  Exported {count} {table} to {output_path}")
        except Exception as e:
            print(f"  Failed to export {table}: {e}")
