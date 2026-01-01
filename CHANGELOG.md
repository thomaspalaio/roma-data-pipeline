# Changelog

All notable changes to Roma Data Pipeline will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-31

### Added

- Initial public release
- Data sources: Pleiades, ORBIS, ToposText, AWMC, Itiner-e, Wikidata
- 35,378 ancient locations with coordinates and metadata
- 186 province boundaries across 4 time periods
- 16,554 Roman road segments
- 2,208 travel network edges with pre-computed travel times
- 106 historical figures (emperors and notable Romans)
- 8,000+ ancient text citations from ToposText
- Full-text search (FTS5) for locations and people
- SQLite, GeoJSON, and CSV export formats
- Command-line interface (`roma-data`)
- Python API for programmatic access
- Temporal filtering (753 BCE to 476 CE)
- Geographic bounding box filtering
- Database validation command
- CITATION.cff for academic citation
- Comprehensive documentation

### Technical

- Python 3.10+ support
- Type hints throughout codebase
- pytest test suite with 80%+ coverage
- GitHub Actions CI/CD pipeline
- PyPI package distribution

[0.1.0]: https://github.com/thomaspalaio/roma-data-pipeline/releases/tag/v0.1.0
