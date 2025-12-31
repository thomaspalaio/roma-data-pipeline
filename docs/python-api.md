# Python API

Use Roma Data Pipeline programmatically in your Python applications.

## Installation

```bash
pip install roma-data-pipeline
```

## Basic Usage

### Running the Pipeline

```python
from roma_data import Pipeline, Config

# Default configuration
pipeline = Pipeline()
db_path = pipeline.run()
print(f"Database created: {db_path}")
```

### Custom Configuration

```python
from pathlib import Path
from roma_data import Pipeline, Config

config = Config(
    # Select sources
    sources=["pleiades", "orbis", "topostext"],

    # Output path
    output_path=Path("./my_database.sqlite"),

    # Working directory for downloads
    output_dir=Path("./roma_data_working"),

    # Use cached downloads
    cache_downloads=True,

    # Verbose logging
    verbose=True,
)

pipeline = Pipeline(config)
db_path = pipeline.run()
```

## Config Class

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class Config:
    sources: List[str]          # Data sources to use
    output_path: Path           # Output database path
    output_dir: Path            # Working directory
    cache_downloads: bool       # Cache downloaded files
    verbose: bool               # Verbose output
```

### Available Sources

- `pleiades` - Pleiades gazetteer (27,000+ locations)
- `orbis` - ORBIS travel network (450 sites, 2,200 edges)
- `topostext` - ToposText places (8,000+ locations)
- `awmc` - AWMC provinces (186 province boundaries)
- `itinere` - Itiner-e roads (16,500+ road segments)
- `wikidata` - Wikidata people and events

## Export Functions

### GeoJSON Export

```python
from pathlib import Path
from roma_data.export.geojson import export_geojson, export_all_geojson

# Export single table
count = export_geojson(
    database=Path("roma_aeterna.sqlite"),
    table="locations",
    output=Path("locations.geojson"),
    verbose=True
)
print(f"Exported {count} features")

# Export all tables
from roma_data import Config
config = Config(output_path=Path("roma_aeterna.sqlite"))
export_all_geojson(config)
```

### CSV Export

```python
from pathlib import Path
from roma_data.export.csv import export_csv, export_all_csv

# Export single table
count = export_csv(
    database=Path("roma_aeterna.sqlite"),
    table="locations",
    output=Path("locations.csv"),
    verbose=True
)
print(f"Exported {count} rows")
```

## Validation

```python
from pathlib import Path
from roma_data.validation.checks import validate_database

results = validate_database(
    database=Path("roma_aeterna.sqlite"),
    verbose=True
)

if results["overall_passed"]:
    print("All checks passed!")
else:
    for error in results["errors"]:
        print(f"Error: {error}")
```

## Querying the Database

```python
import sqlite3
from pathlib import Path

db_path = Path("roma_aeterna.sqlite")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Query locations
cursor = conn.cursor()
cursor.execute("""
    SELECT name_latin, name_modern, type, latitude, longitude
    FROM locations
    WHERE type = 'city'
    ORDER BY name_latin
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row['name_latin']} ({row['name_modern']})")

# Full-text search
cursor.execute("""
    SELECT name_latin, type, description
    FROM location_search
    WHERE location_search MATCH 'temple apollo'
    LIMIT 10
""")

# Query provinces for a time period
cursor.execute("""
    SELECT name_latin, start_year, end_year
    FROM provinces
    WHERE start_year <= -50 AND (end_year IS NULL OR end_year >= -50)
    ORDER BY name_latin
""")

conn.close()
```

## Working with Individual Sources

```python
from roma_data import Config
from roma_data.sources.pleiades import PleiadesSource
from roma_data.sources.orbis import ORBISSource

config = Config()

# Download and transform Pleiades
pleiades = PleiadesSource(config)
pleiades.download()
locations = pleiades.transform()
print(f"Pleiades: {len(locations)} locations")

# Download and transform ORBIS
orbis = ORBISSource(config)
orbis.download()
sites = orbis.transform()
edges = orbis.transform_travel_network()
print(f"ORBIS: {len(sites)} sites, {len(edges)} edges")
```

## Error Handling

```python
from roma_data import Pipeline, Config
from roma_data.exceptions import PipelineError, SourceError

config = Config(sources=["pleiades"])
pipeline = Pipeline(config)

try:
    db_path = pipeline.run()
except SourceError as e:
    print(f"Source download failed: {e}")
except PipelineError as e:
    print(f"Pipeline error: {e}")
```
