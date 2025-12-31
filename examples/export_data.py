#!/usr/bin/env python3
"""
Data export example for Roma Data Pipeline.

This example shows how to export data to different formats:
- GeoJSON (for GIS applications)
- CSV (for spreadsheet analysis)
"""

from pathlib import Path

from roma_data.export.csv import export_csv
from roma_data.export.geojson import export_geojson


def main():
    db_path = Path("./my_database.sqlite")

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Run 'roma-data run' first to generate the database.")
        return

    # Create output directories
    geojson_dir = Path("./exports/geojson")
    csv_dir = Path("./exports/csv")
    geojson_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)

    # Export to GeoJSON
    print("Exporting to GeoJSON...")
    tables = ["locations", "provinces", "roads"]

    for table in tables:
        output = geojson_dir / f"{table}.geojson"
        try:
            count = export_geojson(db_path, table, output, verbose=True)
            print(f"  {table}: {count} features -> {output}")
        except Exception as e:
            print(f"  {table}: Error - {e}")

    # Export to CSV
    print("\nExporting to CSV...")
    tables = ["locations", "provinces", "roads", "people", "events"]

    for table in tables:
        output = csv_dir / f"{table}.csv"
        try:
            count = export_csv(db_path, table, output, verbose=True)
            print(f"  {table}: {count} rows -> {output}")
        except Exception as e:
            print(f"  {table}: Error - {e}")

    print("\nDone! Check the exports/ directory.")

    # Show file sizes
    print("\nExported files:")
    for directory in [geojson_dir, csv_dir]:
        for f in sorted(directory.iterdir()):
            size_kb = f.stat().st_size / 1024
            print(f"  {f.relative_to('.')}: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
