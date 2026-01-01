# Academic Use

Guidelines for using Roma Data Pipeline in academic research.

## Citation

### Software Citation

If you use this software, please cite:

**BibTeX:**

```bibtex
@software{roma_data_pipeline,
  author       = {Roma Data Pipeline Contributors},
  title        = {Roma Data Pipeline: Comprehensive ETL for Roman World Data},
  year         = {2025},
  publisher    = {GitHub},
  url          = {https://github.com/thomaspalaio/roma-data-pipeline},
  version      = {0.1.0}
}
```

**APA:**

> Roma Data Pipeline Contributors. (2025). Roma Data Pipeline: Comprehensive ETL for Roman World Data (Version 0.1.0) [Computer software]. https://github.com/thomaspalaio/roma-data-pipeline

### Data Source Citations

When publishing research using this data, you should also cite the underlying data sources:

**Pleiades:**

```bibtex
@misc{pleiades,
  author       = {{Pleiades Contributors}},
  title        = {Pleiades: A Gazetteer of Past Places},
  url          = {https://pleiades.stoa.org},
  note         = {Accessed: 2025}
}
```

**ORBIS:**

```bibtex
@article{orbis,
  author  = {Scheidel, Walter and Meeks, Elijah},
  title   = {ORBIS: The Stanford Geospatial Network Model of the Roman World},
  year    = {2012},
  url     = {https://orbis.stanford.edu}
}
```

**ToposText:**

```bibtex
@misc{topostext,
  author       = {Kiesling, Brady},
  title        = {ToposText},
  publisher    = {Aikaterini Laskaridis Foundation},
  url          = {https://topostext.org}
}
```

---

## FAIR Principles

This project follows FAIR data principles:

### Findable

- **Persistent Identifier**: GitHub repository with releases
- **Rich Metadata**: CITATION.cff, codemeta.json
- **Indexed**: PyPI package registry

### Accessible

- **Open Protocol**: HTTP/HTTPS download
- **Open Source**: MIT license for code
- **Multiple Formats**: SQLite, GeoJSON, CSV

### Interoperable

- **Standard Formats**: GeoJSON (RFC 7946), CSV, SQLite
- **Linked Data**: Pleiades URIs, Wikidata IDs
- **Coordinate System**: WGS84 (EPSG:4326)

### Reusable

- **Clear License**: MIT (code), CC-BY-4.0 (data output)
- **Documentation**: Comprehensive schema docs
- **Provenance**: Source attribution in metadata

---

## Data Provenance

### Source Attribution

Each record maintains provenance through:

- `id` prefix indicates source (e.g., `pleiades_`, `orbis_`, `topostext_`)
- `pleiades_uri` links to authoritative Pleiades record
- `wikidata_id` links to Wikidata entity

### Processing Methodology

1. **Download**: Raw data fetched from source APIs/downloads
2. **Transform**: Normalized to common schema
3. **Deduplicate**: Cross-source matching by coordinates/names
4. **Enrich**: Spatial indexing, entity linking
5. **Export**: SQLite with FTS5 indexes

### Reproducibility

Pipeline runs are reproducible:

```bash
# Cache downloads for reproducibility
roma-data run --cache --output reproduce.sqlite

# Verify with validation
roma-data validate reproduce.sqlite
```

---

## Methodology Notes

### Coordinate Precision

Coordinates are provided as-is from sources. Precision varies:

- Archaeological sites: typically 10-100m
- Literary references: may be 1-10km
- Regional features: centroid approximations

### Temporal Data

Years use astronomical numbering:

- Positive = CE (1 = 1 CE)
- Negative = BCE (-44 = 44 BCE)
- Zero = 1 BCE

### Location Types

Type mappings are standardized across sources. Original source types are preserved where possible.

### Data Completeness

Not all fields are populated for all records:

- `name_latin`: 95%+ coverage
- `coordinates`: 98%+ coverage (required for export)
- `founding_year`: ~20% coverage
- `wikidata_id`: ~15% coverage

---

## Research Applications

This dataset has been used for:

- Historical GIS visualization
- Network analysis of Roman trade routes
- Spatial analysis of urbanization
- Digital humanities research
- Educational applications

---

## Contact

For academic collaboration or questions:

- GitHub Issues: Report bugs or request features
- Discussions: Ask questions about methodology

## Acknowledgments

This project would not be possible without the foundational work of:

- Pleiades project contributors
- Stanford ORBIS team (Walter Scheidel, Elijah Meeks)
- Brady Kiesling and ToposText
- Ancient World Mapping Center at UNC
- Itiner-e project team
- Wikidata community
