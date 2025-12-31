"""
GeoJSON export for Roma Data Pipeline.

Exports database tables to GeoJSON format for use in GIS applications.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from roma_data.config import Config


def export_geojson(
    database: Path,
    table: str,
    output: Path,
    verbose: bool = False
) -> int:
    """
    Export a table to GeoJSON.

    Args:
        database: Path to SQLite database
        table: Table name to export
        output: Output GeoJSON file path
        verbose: Print verbose output

    Returns:
        Number of features exported
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
    }

    if table not in exporters:
        raise ValueError(f"Unknown table: {table}. Valid: {', '.join(exporters.keys())}")

    features = exporters[table](conn, verbose)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "source": "Roma Data Pipeline",
            "table": table,
            "count": len(features),
        }
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    conn.close()

    if verbose:
        print(f"Exported {len(features)} features to {output}")

    return len(features)


def _export_locations(conn: sqlite3.Connection, verbose: bool) -> List[Dict[str, Any]]:
    """Export locations as GeoJSON Point features."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name_latin, name_modern, type, latitude, longitude,
               description, founding_year, destruction_year, province_id,
               pleiades_uri, wikidata_id, confidence
        FROM locations
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)

    features = []
    for row in cursor.fetchall():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            },
            "properties": {
                "id": row["id"],
                "name_latin": row["name_latin"],
                "name_modern": row["name_modern"],
                "type": row["type"],
                "description": row["description"],
                "founding_year": row["founding_year"],
                "destruction_year": row["destruction_year"],
                "province_id": row["province_id"],
                "pleiades_uri": row["pleiades_uri"],
                "wikidata_id": row["wikidata_id"],
                "confidence": row["confidence"],
            }
        }
        features.append(feature)

    return features


def _export_provinces(conn: sqlite3.Connection, verbose: bool) -> List[Dict[str, Any]]:
    """Export provinces as GeoJSON features with polygon geometry."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, name_latin, start_year, end_year,
               polygon_geojson, centroid_lat, centroid_lon,
               parent_entity, color_hex
        FROM provinces
    """)

    features = []
    for row in cursor.fetchall():
        # Use polygon boundary if available, otherwise centroid point
        if row["polygon_geojson"]:
            try:
                geometry = json.loads(row["polygon_geojson"])
            except json.JSONDecodeError:
                geometry = None
        else:
            geometry = None

        if not geometry and row["centroid_lat"] and row["centroid_lon"]:
            geometry = {
                "type": "Point",
                "coordinates": [row["centroid_lon"], row["centroid_lat"]]
            }

        if not geometry:
            continue

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": row["id"],
                "name": row["name"],
                "name_latin": row["name_latin"],
                "start_year": row["start_year"],
                "end_year": row["end_year"],
                "parent_entity": row["parent_entity"],
                "color_hex": row["color_hex"],
            }
        }
        features.append(feature)

    return features


def _export_roads(conn: sqlite3.Connection, verbose: bool) -> List[Dict[str, Any]]:
    """Export roads as GeoJSON LineString features."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, name_latin, path_geojson, road_type,
               construction_year, abandonment_year, length_km, confidence
        FROM roads
        WHERE path_geojson IS NOT NULL
    """)

    features = []
    for row in cursor.fetchall():
        try:
            geometry = json.loads(row["path_geojson"])
        except json.JSONDecodeError:
            continue

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": row["id"],
                "name": row["name"],
                "name_latin": row["name_latin"],
                "road_type": row["road_type"],
                "construction_year": row["construction_year"],
                "abandonment_year": row["abandonment_year"],
                "length_km": row["length_km"],
                "confidence": row["confidence"],
            }
        }
        features.append(feature)

    return features


def _export_people(conn: sqlite3.Connection, verbose: bool) -> List[Dict[str, Any]]:
    """Export people as GeoJSON features (with birth/death locations if available)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.name_latin, p.birth_year, p.death_year,
               p.role, p.description, p.wikidata_id,
               bl.latitude as birth_lat, bl.longitude as birth_lon,
               dl.latitude as death_lat, dl.longitude as death_lon
        FROM people p
        LEFT JOIN locations bl ON p.birth_location_id = bl.id
        LEFT JOIN locations dl ON p.death_location_id = dl.id
    """)

    features = []
    for row in cursor.fetchall():
        # Use birth location, death location, or skip if neither
        if row["birth_lat"] and row["birth_lon"]:
            geometry = {
                "type": "Point",
                "coordinates": [row["birth_lon"], row["birth_lat"]]
            }
        elif row["death_lat"] and row["death_lon"]:
            geometry = {
                "type": "Point",
                "coordinates": [row["death_lon"], row["death_lat"]]
            }
        else:
            # No geometry, but still include with null geometry
            geometry = None

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": row["id"],
                "name": row["name"],
                "name_latin": row["name_latin"],
                "birth_year": row["birth_year"],
                "death_year": row["death_year"],
                "role": row["role"],
                "description": row["description"],
                "wikidata_id": row["wikidata_id"],
            }
        }
        features.append(feature)

    return features


def _export_events(conn: sqlite3.Connection, verbose: bool) -> List[Dict[str, Any]]:
    """Export events as GeoJSON features."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.name, e.year, e.end_year, e.type,
               e.description, e.outcome, e.significance, e.wikidata_id,
               l.latitude, l.longitude
        FROM events e
        LEFT JOIN locations l ON e.location_id = l.id
    """)

    features = []
    for row in cursor.fetchall():
        if row["latitude"] and row["longitude"]:
            geometry = {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            }
        else:
            geometry = None

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": row["id"],
                "name": row["name"],
                "year": row["year"],
                "end_year": row["end_year"],
                "type": row["type"],
                "description": row["description"],
                "outcome": row["outcome"],
                "significance": row["significance"],
                "wikidata_id": row["wikidata_id"],
            }
        }
        features.append(feature)

    return features


def export_all_geojson(config: "Config") -> None:
    """
    Export all tables to GeoJSON files.

    Args:
        config: Pipeline configuration
    """
    output_dir = config.output_dir / "geojson"
    output_dir.mkdir(parents=True, exist_ok=True)

    database = config.output_path

    tables = ["locations", "provinces", "roads", "people", "events"]

    for table in tables:
        output_path = output_dir / f"{table}.geojson"
        try:
            count = export_geojson(database, table, output_path, config.verbose)
            print(f"  Exported {count} {table} to {output_path}")
        except Exception as e:
            print(f"  Failed to export {table}: {e}")
