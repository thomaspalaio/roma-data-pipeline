# CLI Reference

Complete reference for the `roma-data` command-line interface.

## Commands

### `roma-data run`

Run the complete pipeline: download, transform, and export.

```bash
roma-data run [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output PATH` | Output database path | `roma_aeterna.sqlite` |
| `--sources LIST` | Comma-separated source list | All sources |
| `--cache/--no-cache` | Use cached downloads | `--cache` |
| `--verbose` | Verbose output | Off |
| `--quiet` | Minimal output | Off |

**Examples:**

```bash
# Run with defaults
roma-data run

# Custom output path
roma-data run --output ./data/roman_world.sqlite

# Only Pleiades and ORBIS
roma-data run --sources pleiades,orbis

# Force re-download (no cache)
roma-data run --no-cache

# Verbose logging
roma-data run --verbose
```

### `roma-data validate`

Validate a generated database.

```bash
roma-data validate DATABASE [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `DATABASE` | Path to SQLite database |

**Options:**

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed results |

**Example:**

```bash
roma-data validate roma_aeterna.sqlite --verbose
```

**Validation Checks:**

- Table row counts (minimum thresholds)
- Coordinate validity (lat/lon ranges)
- Required field population
- FTS index functionality
- Data value ranges
- Foreign key relationships

### `roma-data export`

Export database tables to other formats.

```bash
roma-data export FORMAT TABLE OUTPUT [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `FORMAT` | Export format: `geojson` or `csv` |
| `TABLE` | Table to export |
| `OUTPUT` | Output file path |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--database PATH` | Source database | `roma_aeterna.sqlite` |
| `--verbose` | Verbose output | Off |

**Available Tables:**

- `locations` - Ancient places
- `provinces` - Roman provinces
- `roads` - Road segments
- `people` - Historical figures
- `events` - Historical events
- `travel_network` - ORBIS edges
- `timeline_markers` - Timeline events

**Examples:**

```bash
# Export locations to GeoJSON
roma-data export geojson locations ./locations.geojson

# Export roads to CSV
roma-data export csv roads ./roads.csv

# From custom database
roma-data export geojson locations ./out.geojson --database ./custom.sqlite
```

### `roma-data info`

Show information about available sources and configuration.

```bash
roma-data info
```

**Output:**

- Available data sources
- Default configuration
- Version information

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ROMA_DATA_CACHE_DIR` | Cache directory for downloads |
| `ROMA_DATA_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Database not found |
| 4 | Validation failed |
