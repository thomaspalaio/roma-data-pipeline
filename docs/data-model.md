# Data Model

Complete schema documentation for the Roma Data Pipeline SQLite database.

## Overview

The database uses SQLite with FTS5 full-text search indexes. All tables use TEXT primary keys to support cross-referencing with external identifiers (Pleiades URIs, Wikidata IDs).

## Tables

### locations

Ancient places including cities, temples, forts, and geographic features.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Unique identifier (e.g., `pleiades_423025`) |
| `name_latin` | TEXT | Latin/ancient name |
| `name_modern` | TEXT | Modern name |
| `type` | TEXT | Location type (see below) |
| `latitude` | REAL | WGS84 latitude |
| `longitude` | REAL | WGS84 longitude |
| `founding_year` | INTEGER | Year founded (negative = BCE) |
| `destruction_year` | INTEGER | Year destroyed/abandoned |
| `peak_population` | INTEGER | Estimated peak population |
| `province_id` | TEXT | Reference to provinces table |
| `description` | TEXT | Description text |
| `confidence` | TEXT | Location confidence level |
| `pleiades_uri` | TEXT | Pleiades URI |
| `wikidata_id` | TEXT | Wikidata Q-identifier |
| `topostext_url` | TEXT | ToposText URL |

**Location Types:**

- `city`, `settlement`, `village`
- `temple`, `sanctuary`
- `fort`, `fortress`, `military-camp`
- `port`, `harbor`
- `bridge`, `aqueduct`
- `villa`, `palace`, `bath`
- `theater`, `stadium`, `amphitheater`
- `mountain`, `river`, `lake`, `island`
- `mine`, `quarry`
- `cemetery`, `tomb`
- `road`, `milestone`
- `region`, `other`

**Indexes:**

- `idx_locations_coords` on (latitude, longitude)
- `idx_locations_type` on (type)

### provinces

Roman provinces with temporal boundaries.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Unique identifier |
| `name` | TEXT | Display name |
| `name_latin` | TEXT | Latin name |
| `start_year` | INTEGER | Year province established |
| `end_year` | INTEGER | Year province dissolved |
| `polygon_geojson` | TEXT | GeoJSON polygon geometry |
| `centroid_lat` | REAL | Centroid latitude |
| `centroid_lon` | REAL | Centroid longitude |
| `parent_entity` | TEXT | Parent administrative unit |
| `color_hex` | TEXT | Display color |

### roads

Roman road segments with geometry.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Unique identifier |
| `name` | TEXT | Road name |
| `name_latin` | TEXT | Latin name |
| `path_geojson` | TEXT | GeoJSON LineString geometry |
| `construction_year` | INTEGER | Year constructed |
| `abandonment_year` | INTEGER | Year abandoned |
| `length_km` | REAL | Length in kilometers |
| `road_type` | TEXT | Road type (major, secondary, etc.) |
| `confidence` | TEXT | Data confidence |
| `itinere_id` | TEXT | Itiner-e reference |

### people

Historical figures (emperors, senators, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Unique identifier |
| `name` | TEXT | Common name |
| `name_latin` | TEXT | Latin name |
| `birth_year` | INTEGER | Birth year |
| `death_year` | INTEGER | Death year |
| `birth_location_id` | TEXT | Reference to locations |
| `death_location_id` | TEXT | Reference to locations |
| `role` | TEXT | Primary role (emperor, senator, etc.) |
| `description` | TEXT | Biography |
| `wikidata_id` | TEXT | Wikidata Q-identifier |

### events

Historical events (battles, treaties, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Unique identifier |
| `name` | TEXT | Event name |
| `year` | INTEGER | Start year |
| `end_year` | INTEGER | End year (for multi-year events) |
| `type` | TEXT | Event type |
| `location_id` | TEXT | Reference to locations |
| `description` | TEXT | Description |
| `outcome` | TEXT | Outcome/result |
| `significance` | INTEGER | Significance score (1-10) |
| `wikidata_id` | TEXT | Wikidata Q-identifier |

### travel_network

ORBIS travel network edges for route calculation.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Edge identifier |
| `source_location_id` | TEXT | Start location |
| `target_location_id` | TEXT | End location |
| `source_name` | TEXT | Start location name |
| `target_name` | TEXT | End location name |
| `distance_km` | REAL | Distance in kilometers |
| `travel_days_foot` | REAL | Travel time on foot |
| `travel_days_horse` | REAL | Travel time by horse |
| `travel_days_cart` | REAL | Travel time by cart |
| `travel_days_ship` | REAL | Travel time by ship |
| `cost_denarii_per_kg` | REAL | Transport cost |
| `seasonal` | INTEGER | Is route seasonal (0/1) |
| `data_source` | TEXT | Data source (orbis) |

### timeline_markers

Key dates for timeline visualization.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment ID |
| `year` | INTEGER | Year |
| `name` | TEXT | Event name |
| `description` | TEXT | Description |
| `marker_type` | TEXT | Marker type (major, minor) |

## Full-Text Search

### location_search

FTS5 virtual table for location search.

```sql
-- Search for locations
SELECT name_latin, type
FROM location_search
WHERE location_search MATCH 'forum rome';

-- Ranked search
SELECT name_latin, type, rank
FROM location_search
WHERE location_search MATCH 'temple'
ORDER BY rank;
```

## Year Convention

All years use astronomical year numbering:

- Positive integers = CE (e.g., 100 = 100 CE)
- Negative integers = BCE (e.g., -44 = 44 BCE)
- Zero = 1 BCE (astronomical convention)

## Coordinate System

All coordinates use WGS84 (EPSG:4326):

- Latitude: -90 to 90
- Longitude: -180 to 180
