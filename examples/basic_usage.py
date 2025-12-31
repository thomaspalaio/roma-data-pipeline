#!/usr/bin/env python3
"""
Basic usage example for Roma Data Pipeline.

This example shows how to:
1. Run the pipeline programmatically
2. Query the generated database
3. Export data to different formats
"""

from pathlib import Path
from roma_data import Pipeline, Config


def main():
    # Create a configuration (defaults work for most use cases)
    config = Config(
        output_path=Path("./my_database.sqlite"),
        sources=["pleiades", "orbis", "topostext"],  # Select sources
        verbose=True,
    )

    # Create and run the pipeline
    pipeline = Pipeline(config)
    print("Running Roma Data Pipeline...")

    # Run all stages: download, transform, export
    db_path = pipeline.run()
    print(f"\nDatabase created: {db_path}")

    # Query the database
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count locations by type
    print("\nLocations by type:")
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM locations
        GROUP BY type
        ORDER BY count DESC
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Find major cities
    print("\nMajor Roman cities (settlements with population data):")
    cursor.execute("""
        SELECT name_latin, name_modern, peak_population
        FROM locations
        WHERE peak_population IS NOT NULL
        ORDER BY peak_population DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]} ({row[1]}): {row[2]:,} people")

    # Search using FTS
    print("\nFull-text search for 'forum':")
    cursor.execute("""
        SELECT name_latin, type
        FROM location_search
        WHERE location_search MATCH 'forum'
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]} ({row[1]})")

    conn.close()


if __name__ == "__main__":
    main()
