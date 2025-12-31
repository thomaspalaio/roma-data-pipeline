# Quick Start

Get up and running with Roma Data Pipeline in 5 minutes.

## Installation

```bash
pip install roma-data-pipeline
```

**Requirements**: Python 3.10+

## Basic Usage

### Generate the Database

```bash
# Run with all sources (takes ~5 minutes)
roma-data run

# Output: roma_aeterna.sqlite in current directory
```

### Customize Output

```bash
# Custom output path
roma-data run --output ./my_database.sqlite

# Select specific sources
roma-data run --sources pleiades,orbis

# Verbose output
roma-data run --verbose
```

### Validate the Database

```bash
roma-data validate roma_aeterna.sqlite
```

### Export to Other Formats

```bash
# Export locations to GeoJSON
roma-data export geojson locations ./locations.geojson

# Export roads to CSV
roma-data export csv roads ./roads.csv
```

## Python API

```python
from roma_data import Pipeline, Config

# Simple usage
pipeline = Pipeline()
db_path = pipeline.run()

# Custom configuration
config = Config(
    sources=["pleiades", "orbis", "topostext"],
    output_path="./custom.sqlite",
    verbose=True,
)
pipeline = Pipeline(config)
db_path = pipeline.run()
```

## Query the Database

```python
import sqlite3

conn = sqlite3.connect("roma_aeterna.sqlite")
cursor = conn.cursor()

# Find all cities
cursor.execute("""
    SELECT name_latin, latitude, longitude
    FROM locations
    WHERE type = 'city'
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}, {row[2]}")

# Full-text search
cursor.execute("""
    SELECT name_latin, type
    FROM location_search
    WHERE location_search MATCH 'forum'
""")
```

## Next Steps

- [CLI Reference](cli-reference.md) - All command-line options
- [Python API](python-api.md) - Programmatic usage
- [Data Model](data-model.md) - Database schema
- [Data Sources](data-sources.md) - Source documentation
