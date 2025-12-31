# Data Sources

Detailed documentation of all data sources used by Roma Data Pipeline.

## Overview

| Source | Records | License | URL |
|--------|---------|---------|-----|
| Pleiades | 27,000+ locations | CC-BY-3.0 | pleiades.stoa.org |
| ORBIS | 450 sites, 2,200 edges | Open | orbis.stanford.edu |
| ToposText | 8,000+ places | CC-BY-NC-SA | topostext.org |
| AWMC | 186 provinces | CC-BY-NC | awmc.unc.edu |
| Itiner-e | 16,500+ road segments | Open | itiner-e.org |
| Wikidata | 100+ people/events | CC0 | wikidata.org |

---

## Pleiades

**Pleiades: A Gazetteer of Past Places**

The primary source for ancient place data. Pleiades is a community-built gazetteer of ancient places, providing stable URIs and coordinates for over 35,000 places in the ancient world.

- **URL**: https://pleiades.stoa.org
- **License**: CC-BY-3.0
- **Data Format**: JSON dump
- **Records**: ~27,000 locations with coordinates

**Data Provided:**

- Location names (Latin, Greek, modern)
- Coordinates (WGS84)
- Place types
- Time periods
- Connections to other places
- Bibliography

**Attribution:**

> Pleiades: A Gazetteer of Past Places. https://pleiades.stoa.org

---

## ORBIS

**ORBIS: The Stanford Geospatial Network Model of the Roman World**

Provides travel network data including distances and travel times between major Roman sites.

- **URL**: https://orbis.stanford.edu
- **Data Source**: github.com/sfsheath/gorbit
- **License**: Open (academic use)
- **Records**: 450 sites, 2,208 travel edges

**Data Provided:**

- Network nodes (major cities)
- Travel edges with distances
- Travel times (foot, horse, cart, ship)
- Route types (road, river, sea)

**Attribution:**

> Scheidel, W. and Meeks, E. (2012). ORBIS: The Stanford Geospatial Network Model of the Roman World.

---

## ToposText

**ToposText: A Portal to Ancient Places**

Links ancient texts to geographic locations, providing rich citation data from classical literature.

- **URL**: https://topostext.org
- **License**: CC-BY-NC-SA-4.0
- **Data Format**: GeoJSON
- **Records**: 8,000+ places

**Data Provided:**

- Location names and coordinates
- Links to ancient text citations
- Cross-references to Pleiades and Wikidata
- Citation counts from classical sources

**Attribution:**

> Kiesling, B. ToposText. Aikaterini Laskaridis Foundation. https://topostext.org

---

## AWMC

**Ancient World Mapping Center**

Provides historical province boundaries for different time periods.

- **URL**: http://awmc.unc.edu
- **GitHub**: github.com/AWMC/geodata
- **License**: CC-BY-NC-3.0
- **Records**: 186 province boundaries

**Data Provided:**

- Province polygons (GeoJSON)
- Temporal boundaries (start/end years)
- Province names (Latin)

**Attribution:**

> Ancient World Mapping Center. University of North Carolina at Chapel Hill. http://awmc.unc.edu

---

## Itiner-e

**Itiner-e: Roman Roads Digital Atlas**

Comprehensive digital atlas of Roman roads.

- **URL**: https://itiner-e.org
- **License**: Open
- **Data Format**: GeoJSON (NDJSON)
- **Records**: 16,500+ road segments

**Data Provided:**

- Road geometries (LineStrings)
- Road names
- Road types
- Connection points

**Attribution:**

> Itiner-e Project. https://itiner-e.org

---

## Wikidata

**Wikidata Knowledge Base**

Provides structured data about Roman emperors, notable figures, and historical events.

- **URL**: https://www.wikidata.org
- **License**: CC0
- **Query Method**: SPARQL
- **Records**: 100+ people, events

**Data Provided:**

- Roman emperors with dates
- Notable figures
- Historical battles and events
- Cross-references

**SPARQL Queries:**

The pipeline uses custom SPARQL queries to extract:

1. Roman emperors (P39 = Q842606)
2. Ancient Roman senators
3. Roman battles (P31 = Q178561)

**Attribution:**

> Wikidata contributors. Wikidata. https://www.wikidata.org

---

## Data Quality

### Confidence Levels

Locations include confidence ratings:

- `certain` - Confirmed archaeological identification
- `probable` - High confidence based on evidence
- `possible` - Plausible identification
- `approximate` - General area known

### Coordinate Accuracy

Coordinate precision varies by source:

| Source | Typical Accuracy |
|--------|------------------|
| Pleiades | 10-100m (confirmed sites) |
| ORBIS | 100m-1km (network nodes) |
| ToposText | 100m-1km |
| AWMC | Province-level polygons |

### Temporal Coverage

The data primarily covers:

- Geographic scope: Mediterranean, Western Europe, Near East
- Temporal scope: ~1000 BCE to 500 CE
- Focus period: Roman Republic and Empire (509 BCE - 476 CE)

---

## License Compliance

When using data from Roma Data Pipeline, you must comply with source licenses:

1. **Pleiades (CC-BY)**: Attribute Pleiades project
2. **ToposText (CC-BY-NC-SA)**: Non-commercial use, share-alike
3. **AWMC (CC-BY-NC)**: Non-commercial use, attribute AWMC
4. **Wikidata (CC0)**: No restrictions

For commercial use, consult individual source licenses.
