# Roma Data Pipeline

> Comprehensive ETL pipeline for Roman world data from Pleiades, ORBIS, Wikidata, and more.

[![PyPI version](https://badge.fury.io/py/roma-data-pipeline.svg)](https://badge.fury.io/py/roma-data-pipeline)
[![CI](https://github.com/thomaspalaio/roma-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/thomaspalaio/roma-data-pipeline/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Data License: CC-BY-4.0](https://img.shields.io/badge/Data-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Roma Data Pipeline** generates a unified SQLite database containing **35,000+ ancient locations**, **16,500+ Roman roads**, **100+ historical figures**, and **pre-computed travel times** across the Roman Empire. It aggregates, transforms, links, and exports data from multiple authoritative academic sources into a single, queryable dataset.

## Quick Start

```bash
pip install roma-data-pipeline
roma-data run
# Or if roma-data isn't in your PATH:
python -m roma_data run
```

This creates `roma_aeterna.sqlite` in your current directory (~50 MB).

## What's Inside

| Data | Records | Source |
|------|---------|--------|
| Ancient locations | 35,378 | [Pleiades](https://pleiades.stoa.org), [ORBIS](https://orbis.stanford.edu), [ToposText](https://topostext.org) |
| Province boundaries | 186 | [AWMC](https://github.com/AWMC/geodata) |
| Roman roads | 16,554 | [Itiner-e](https://itiner-e.org) |
| Historical people | 106 | [Wikidata](https://www.wikidata.org) |
| Travel network | 2,208 edges | [ORBIS](https://orbis.stanford.edu) |
| Ancient text citations | 8,000+ | [ToposText](https://topostext.org) |

## Features

- **8 Authoritative Sources**: Aggregates data from Pleiades, AWMC, Itiner-e, Wikidata, ORBIS, and ToposText
- **Full-Text Search**: FTS5-powered search across locations and people
- **Travel Time Calculator**: ORBIS-derived travel times by foot, horse, cart, or ship
- **Temporal Filtering**: Filter by date range (753 BCE to 476 CE)
- **Geographic Filtering**: Filter by bounding box
- **Multiple Export Formats**: SQLite, GeoJSON, CSV
- **Academic-Ready**: DOI, CITATION.cff, FAIR principles compliant

## Installation

### From PyPI

```bash
pip install roma-data-pipeline
```

### From Source

```bash
git clone https://github.com/thomaspalaio/roma-data-pipeline
cd roma-data-pipeline
pip install -e ".[dev]"
```

## Usage

### Command Line

```bash
# Run full pipeline (creates roma_aeterna.sqlite)
roma-data run

# Custom output path
roma-data run --output ./my_database.sqlite

# Select specific data sources
roma-data run --sources pleiades,orbis,wikidata

# Filter by time period (200 BCE to 200 CE)
roma-data run --start-year -200 --end-year 200

# Filter by geographic region (Western Mediterranean)
roma-data run --bbox "-10,35,20,50"

# Export to GeoJSON
roma-data export geojson locations.geojson

# Validate a database
roma-data validate ./roma_aeterna.sqlite

# Show available sources
roma-data info
```

### Python API

```python
from roma_data import Pipeline, Config

# Simple usage
pipeline = Pipeline()
db_path = pipeline.run()

# Custom configuration
config = Config(
    sources=["pleiades", "wikidata", "orbis"],
    output_path="./custom.sqlite",
    time_range=(-200, 200),
    bbox=(-10, 35, 20, 50),
)
Pipeline(config).run()
```

### Query the Database

```python
import sqlite3

conn = sqlite3.connect("roma_aeterna.sqlite")

# Find cities near Rome
cursor = conn.execute("""
    SELECT name_latin, type, latitude, longitude
    FROM locations
    WHERE type = 'city'
    AND ABS(latitude - 41.9) < 1
    AND ABS(longitude - 12.5) < 1
""")
for row in cursor:
    print(row)

# Search for temples
cursor = conn.execute("""
    SELECT name_latin FROM location_search
    WHERE location_search MATCH 'temple apollo'
""")

# Get travel time Rome to Carthage
cursor = conn.execute("""
    SELECT travel_days_ship, travel_days_foot
    FROM travel_network
    WHERE source_name LIKE '%Roma%'
    AND target_name LIKE '%Carthag%'
""")
```

## Data Sources

| Source | Description | License |
|--------|-------------|---------|
| [Pleiades](https://pleiades.stoa.org) | Ancient place gazetteer with 30,000+ locations | CC-BY-3.0 |
| [AWMC](https://github.com/AWMC/geodata) | Province boundaries at 4 time periods | CC-BY-NC-3.0 |
| [Itiner-e](https://itiner-e.org) | Roman road network GIS data | Open |
| [Wikidata](https://www.wikidata.org) | Structured data for people, events, infrastructure | CC0 |
| [ORBIS](https://orbis.stanford.edu) | Stanford's Roman travel network model | Open |
| [ToposText](https://topostext.org) | Ancient text citations by location | CC-BY-NC-SA-4.0 |

## Database Schema

The output SQLite database contains these tables:

- `locations` - Ancient places with coordinates, types, and dates
- `provinces` - Administrative boundaries with GeoJSON polygons
- `roads` - Roman road segments with GeoJSON paths
- `people` - Historical figures with birth/death dates and locations
- `events` - Battles, treaties, disasters with dates and locations
- `travel_network` - Pre-computed travel routes with times and costs
- `ancient_sources` - ToposText citations per location
- `timeline_markers` - Major historical milestones
- `location_search` - FTS5 full-text search index
- `people_search` - FTS5 full-text search index

See [docs/data-model.md](docs/data-model.md) for full schema documentation.

## Citation

If you use this software in academic work, please cite:

```bibtex
@software{roma_data_pipeline,
  author = {Palaio, Thomas},
  title = {Roma Data Pipeline},
  year = {2025},
  url = {https://github.com/thomaspalaio/roma-data-pipeline},
  version = {0.1.0}
}
```

Also cite the underlying data sources as appropriate for your use case.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding a New Data Source

1. Create a new module in `src/roma_data/sources/`
2. Implement the `DataSource` base class
3. Add SPARQL queries or download URLs to `constants.py`
4. Update the CLI and pipeline to include the new source
5. Add tests and documentation

## License

- **Code**: [MIT License](LICENSE)
- **Data outputs**: [CC-BY 4.0](LICENSE-DATA)

The generated data aggregates information from sources with various licenses (CC-BY, CC0, ODbL). See [LICENSE-DATA](LICENSE-DATA) for attribution requirements.

## Acknowledgments

This project builds on the work of many scholars and institutions:

- [Pleiades](https://pleiades.stoa.org) - NYU Institute for the Study of the Ancient World
- [ORBIS](https://orbis.stanford.edu) - Stanford University
- [AWMC](http://awmc.unc.edu) - University of North Carolina at Chapel Hill
- [Itiner-e](https://itiner-e.org) - Roman roads research project
- [ToposText](https://topostext.org) - Brady Kiesling
- [Wikidata](https://www.wikidata.org) - Wikimedia Foundation

## Links

- [PyPI Package](https://pypi.org/project/roma-data-pipeline/)
- [Issue Tracker](https://github.com/thomaspalaio/roma-data-pipeline/issues)
- [Changelog](CHANGELOG.md)
