#!/usr/bin/env python3
"""
Custom filtering example for Roma Data Pipeline.

This example shows how to filter data by:
- Geographic bounding box
- Time period
- Location type
- Province
"""

import sqlite3
from pathlib import Path


def query_by_bounding_box(conn, min_lat: float, max_lat: float,
                          min_lon: float, max_lon: float):
    """Query locations within a geographic bounding box."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name_latin, name_modern, type, latitude, longitude
        FROM locations
        WHERE latitude BETWEEN ? AND ?
        AND longitude BETWEEN ? AND ?
        ORDER BY name_latin
        LIMIT 20
    """, (min_lat, max_lat, min_lon, max_lon))
    return cursor.fetchall()


def query_by_time_period(conn, start_year: int, end_year: int):
    """Query locations active during a time period."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name_latin, type, founding_year, destruction_year
        FROM locations
        WHERE (founding_year IS NULL OR founding_year <= ?)
        AND (destruction_year IS NULL OR destruction_year >= ?)
        ORDER BY founding_year
        LIMIT 20
    """, (end_year, start_year))
    return cursor.fetchall()


def query_by_type(conn, location_type: str):
    """Query locations of a specific type."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name_latin, name_modern, latitude, longitude
        FROM locations
        WHERE type = ?
        ORDER BY name_latin
        LIMIT 20
    """, (location_type,))
    return cursor.fetchall()


def query_roads_by_province(conn, province_name: str):
    """Query roads that pass through a province's territory."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT r.name, r.name_latin, r.length_km, r.road_type
        FROM roads r
        JOIN road_cities rc ON r.id = rc.road_id
        JOIN locations l ON rc.location_id = l.id
        WHERE l.province_id LIKE ?
        ORDER BY r.name
        LIMIT 20
    """, (f"%{province_name}%",))
    return cursor.fetchall()


def main():
    db_path = Path("./my_database.sqlite")

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Run 'roma-data run' first to generate the database.")
        return

    conn = sqlite3.connect(db_path)

    # Example 1: Locations in Italy
    print("=" * 60)
    print("Locations in central Italy (bounding box)")
    print("=" * 60)
    results = query_by_bounding_box(conn, 40.0, 44.0, 10.0, 15.0)
    for row in results:
        print(f"  {row[0]} ({row[2]}): {row[3]:.2f}, {row[4]:.2f}")

    # Example 2: Locations during the Republic
    print("\n" + "=" * 60)
    print("Locations active during the Republic (509 BCE - 27 BCE)")
    print("=" * 60)
    results = query_by_time_period(conn, -509, -27)
    for row in results:
        founded = row[2] if row[2] else "?"
        destroyed = row[3] if row[3] else "?"
        print(f"  {row[0]} ({row[1]}): {founded} - {destroyed}")

    # Example 3: Temples
    print("\n" + "=" * 60)
    print("Temples")
    print("=" * 60)
    results = query_by_type(conn, "temple")
    for row in results:
        modern = row[1] if row[1] else "unknown"
        print(f"  {row[0]} (modern: {modern})")

    # Example 4: Military forts
    print("\n" + "=" * 60)
    print("Military forts")
    print("=" * 60)
    results = query_by_type(conn, "fort")
    for row in results:
        modern = row[1] if row[1] else "unknown"
        print(f"  {row[0]} (modern: {modern})")

    # Example 5: Location types distribution
    print("\n" + "=" * 60)
    print("Location types distribution")
    print("=" * 60)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM locations
        GROUP BY type
        ORDER BY count DESC
        LIMIT 15
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()


if __name__ == "__main__":
    main()
