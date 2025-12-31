# Roma Data Pipeline

**Comprehensive ETL for Roman world data from Pleiades, ORBIS, Wikidata, and more.**

Roma Data Pipeline aggregates, transforms, and exports data about the ancient Roman world from multiple authoritative academic sources into a unified SQLite database ready for research, visualization, and application development.

## Features

- **8 Authoritative Sources**: Pleiades, ORBIS, Wikidata, AWMC, Itiner-e, ToposText
- **35,000+ Locations**: Cities, temples, forts, roads, and geographic features
- **16,500+ Road Segments**: Complete Roman road network with geometry
- **Travel Calculations**: Pre-computed travel times from ORBIS network model
- **Full-Text Search**: FTS5 indexes for fast location search
- **Multiple Exports**: SQLite, GeoJSON, CSV formats
- **Academic Ready**: DOI, CITATION.cff, data provenance documentation

## Quick Start

```bash
# Install
pip install roma-data-pipeline

# Run pipeline (creates roma_aeterna.sqlite)
roma-data run

# Validate output
roma-data validate roma_aeterna.sqlite
```

## Output

The pipeline produces a SQLite database with:

| Table | Records | Description |
|-------|---------|-------------|
| locations | 35,000+ | Ancient places with coordinates |
| roads | 16,500+ | Road segments with geometry |
| provinces | 186 | Roman provinces with boundaries |
| people | 100+ | Emperors, senators, notable figures |
| travel_network | 2,200+ | ORBIS travel time edges |

## Data Sources

All data is sourced from established academic projects:

- [Pleiades](https://pleiades.stoa.org) - Gazetteer of ancient places (CC-BY)
- [ORBIS](https://orbis.stanford.edu) - Stanford travel network model
- [ToposText](https://topostext.org) - Ancient text citations
- [AWMC](http://awmc.unc.edu) - Ancient World Mapping Center
- [Wikidata](https://www.wikidata.org) - Structured knowledge base

## License

- **Code**: MIT License
- **Data Output**: CC-BY-4.0 (requires attribution to source projects)

## Citation

If you use this software in academic work, please cite:

```bibtex
@software{roma_data_pipeline,
  title = {Roma Data Pipeline},
  author = {Roma Data Pipeline Contributors},
  year = {2025},
  url = {https://github.com/romadatapipeline/roma-data-pipeline}
}
```

See [Academic Use](academic-use.md) for detailed citation guidelines.
