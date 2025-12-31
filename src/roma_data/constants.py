"""
Constants and mappings for Roma Data Pipeline.

Contains all URLs, type mappings, SPARQL queries, and other constants
used throughout the pipeline.
"""

from __future__ import annotations

# =============================================================================
# DATA SOURCE URLs
# =============================================================================

# Pleiades Gazetteer - Daily JSON dump (~50MB compressed)
PLEIADES_JSON_URL = "https://atlantides.org/downloads/pleiades/json/pleiades-places-latest.json.gz"

# AWMC Province Boundaries (GeoJSON)
AWMC_BASE_URL = "https://raw.githubusercontent.com/AWMC/geodata/master/Cultural-Data/political_shading"
AWMC_PROVINCE_URLS = {
    "roman_empire_bce_60": f"{AWMC_BASE_URL}/roman_empire_bce_60/roman_empire_bce_60.geojson",
    "roman_empire_ce_117": f"{AWMC_BASE_URL}/roman_empire_ce_117_extent/roman_empire_ce_117_extent.geojson",
    "roman_empire_ce_200": f"{AWMC_BASE_URL}/roman_empire_ce_200_provinces/roman_empire_ce_200_provinces.geojson",
    "roman_empire_post_diocletian": f"{AWMC_BASE_URL}/roman_empire_provinces_post_diocletian/roman_empire_provinces_post_diocletian.geojson",
}

# Itiner-e Roman Roads
ITINERE_DOWNLOAD_URL = "https://itiner-e.org/route-segments/download"

# Wikidata SPARQL endpoint
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# ORBIS Travel Network (via sfsheath/gorbit - curated ORBIS data)
# Source: https://github.com/sfsheath/gorbit
ORBIS_SITES_URL = "https://raw.githubusercontent.com/sfsheath/gorbit/master/gorbit-sites.csv"
ORBIS_EDGES_URL = "https://raw.githubusercontent.com/sfsheath/gorbit/master/gorbit-edges.csv"

# ToposText Ancient Places GeoJSON
# Source: https://topostext.org/TT-downloads
TOPOSTEXT_PLACES_URL = "https://topostext.org/downloads/ToposText_places_2025-11-20.geojson"
TOPOSTEXT_CITATIONS_URL = "https://topostext.org/downloads/ToposTextGazetteer.jsonld"

# =============================================================================
# TIME PERIOD CONSTANTS
# =============================================================================

# Year range for Roman period
ROMAN_START_YEAR = -753  # Founding of Rome
ROMAN_END_YEAR = 476     # Fall of Western Empire

# Pleiades time period identifiers for Roman era
ROMAN_TIME_PERIODS = frozenset({
    "roman-republic",
    "roman-early-empire",
    "roman-late-empire",
    "late-antique",
    "roman",
    "hellenistic-republican",
})

# Map Pleiades time period identifiers to approximate year ranges
PERIOD_TO_YEARS: dict[str, tuple[int, int]] = {
    # Bronze Age
    "bronze-age": (-3000, -1200),
    "middle-bronze-age": (-2000, -1600),
    "late-bronze-age": (-1600, -1200),
    # Iron Age / Archaic
    "iron-age": (-1200, -550),
    "archaic": (-750, -480),
    # Classical
    "classical": (-480, -323),
    # Hellenistic
    "hellenistic": (-323, -31),
    "hellenistic-republican": (-323, -31),
    # Roman Republic
    "roman-republic": (-509, -27),
    "republican": (-509, -27),
    # Roman Empire
    "roman": (-27, 476),
    "roman-early-empire": (-27, 284),
    "roman-principate": (-27, 284),
    # Late Empire
    "roman-late-empire": (284, 476),
    # Late Antique / Byzantine
    "late-antique": (284, 640),
    "byzantine": (330, 1453),
    # Generic centuries
    "1st-century-bce": (-100, -1),
    "2nd-century-bce": (-200, -100),
    "1st-century-ce": (1, 100),
    "2nd-century-ce": (100, 200),
    "3rd-century-ce": (200, 300),
    "4th-century-ce": (300, 400),
    "5th-century-ce": (400, 500),
}

# =============================================================================
# LOCATION TYPE MAPPING
# =============================================================================

# Map Pleiades place types to standardized app types
LOCATION_TYPE_MAP: dict[str, str] = {
    # Cities
    "settlement": "city",
    "settlement-modern": "city",
    "urban": "city",
    "city": "city",
    "colonia": "city",
    "municipium": "city",
    # Ports
    "port": "port",
    "harbor": "port",
    "harbour": "port",
    # Forts
    "fort": "fort",
    "station": "fort",
    "castrum": "fort",
    "fortress": "fort",
    # Temples
    "temple": "temple",
    "sanctuary": "temple",
    "shrine": "temple",
    # Villas
    "villa": "villa",
    "estate": "villa",
    # Amphitheaters
    "amphitheatre": "amphitheater",
    "amphitheater": "amphitheater",
    "arena": "amphitheater",
    # Aqueducts
    "aqueduct": "aqueduct",
    # Baths
    "bath": "bath",
    "thermae": "bath",
    "baths": "bath",
    # Bridges
    "bridge": "bridge",
    "pons": "bridge",
    # Circuses
    "circus": "circus",
    "hippodrome": "circus",
    # Forums
    "forum": "forum",
    "agora": "forum",
    # Lighthouses
    "lighthouse": "lighthouse",
    "pharos": "lighthouse",
    # Theaters
    "theatre": "theater",
    "theater": "theater",
    "odeon": "theater",
    # Settlements (smaller)
    "village": "settlement",
    "vicus": "settlement",
    "oppidum": "settlement",
    # Default
    "default": "other",
}

# Location type priority for disambiguation
LOCATION_TYPE_PRIORITY: dict[str, int] = {
    "city": 1,
    "port": 2,
    "settlement": 3,
    "fort": 4,
    "temple": 5,
    "villa": 6,
    "other": 7,
}

# =============================================================================
# CONFIDENCE MAPPING
# =============================================================================

CONFIDENCE_MAP: dict[str, str] = {
    # Pleiades
    "certain": "confirmed",
    "confident": "confirmed",
    "precise": "confirmed",
    "less-certain": "probable",
    "rough": "probable",
    "uncertain": "uncertain",
    "unlocated": "uncertain",
    # Itiner-e
    "Certain": "confirmed",
    "Conjectured": "probable",
    "Hypothetical": "uncertain",
    # Default
    "default": "probable",
}

# =============================================================================
# ROAD MAPPING
# =============================================================================

ROAD_TYPE_MAP: dict[str, str] = {
    "Main road": "via_publica",
    "main": "via_publica",
    "Secondary road": "secondary",
    "secondary": "secondary",
    "local": "local",
    "default": "secondary",
}

# Known road construction dates
KNOWN_ROAD_DATES: dict[str, int] = {
    "via appia": -312,
    "via latina": -350,
    "via salaria": -361,
    "via flaminia": -220,
    "via aurelia": -241,
    "via aemilia": -187,
    "via postumia": -148,
    "via egnatia": -146,
    "via domitia": -118,
    "via augusta": -8,
    "via traiana": 109,
}

# =============================================================================
# TRAVEL NETWORK CONSTANTS
# =============================================================================

# Travel speeds (km per day)
TRAVEL_SPEEDS: dict[str, int] = {
    "foot": 30,
    "horse": 50,
    "cart": 20,
    "ship": 100,
}

# Seasonal factors for sea travel
SEA_SEASONAL_FACTORS: dict[str, float] = {
    "jan": 2.0,  # Mare clausum
    "feb": 1.8,
    "mar": 1.3,
    "apr": 1.0,
    "may": 1.0,
    "jun": 1.0,
    "jul": 1.0,
    "aug": 1.0,
    "sep": 1.0,
    "oct": 1.2,
    "nov": 1.5,
    "dec": 2.0,  # Mare clausum
}

# =============================================================================
# DATABASE SCHEMA
# =============================================================================

CREATE_TABLES_SQL = """
-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    name_latin TEXT NOT NULL,
    name_modern TEXT,
    type TEXT NOT NULL DEFAULT 'other',
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    founding_year INTEGER,
    destruction_year INTEGER,
    peak_population INTEGER,
    province_id TEXT,
    parent_location_id TEXT,
    description TEXT,
    thumbnail_filename TEXT,
    confidence TEXT NOT NULL DEFAULT 'probable',
    pleiades_uri TEXT,
    wikidata_id TEXT,
    ancient_text_refs INTEGER,
    ancient_text_count INTEGER,
    topostext_url TEXT
);

-- Provinces table
CREATE TABLE IF NOT EXISTS provinces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_latin TEXT NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER,
    polygon_geojson TEXT NOT NULL,
    centroid_lat REAL,
    centroid_lon REAL,
    parent_entity TEXT,
    color_hex TEXT
);

-- Roads table
CREATE TABLE IF NOT EXISTS roads (
    id TEXT PRIMARY KEY,
    name TEXT,
    name_latin TEXT,
    path_geojson TEXT NOT NULL,
    construction_year INTEGER,
    abandonment_year INTEGER,
    length_km REAL,
    road_type TEXT NOT NULL DEFAULT 'secondary',
    confidence TEXT NOT NULL DEFAULT 'probable',
    itinere_id TEXT
);

-- People table
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_latin TEXT,
    birth_year INTEGER,
    death_year INTEGER,
    birth_location_id TEXT,
    death_location_id TEXT,
    role TEXT,
    description TEXT,
    wikidata_id TEXT
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    year INTEGER NOT NULL,
    end_year INTEGER,
    type TEXT NOT NULL DEFAULT 'other',
    location_id TEXT,
    description TEXT,
    outcome TEXT,
    significance INTEGER,
    wikidata_id TEXT
);

-- Travel network table
CREATE TABLE IF NOT EXISTS travel_network (
    id TEXT PRIMARY KEY,
    source_location_id TEXT NOT NULL,
    target_location_id TEXT NOT NULL,
    source_name TEXT,
    target_name TEXT,
    distance_km REAL NOT NULL,
    travel_days_foot REAL,
    travel_days_horse REAL,
    travel_days_cart REAL,
    travel_days_ship REAL,
    cost_denarii_per_kg REAL,
    seasonal INTEGER NOT NULL DEFAULT 0,
    data_source TEXT NOT NULL DEFAULT 'orbis'
);

-- Ancient sources table
CREATE TABLE IF NOT EXISTS ancient_sources (
    id TEXT PRIMARY KEY,
    location_id TEXT,
    location_name TEXT,
    topostext_url TEXT,
    reference_count INTEGER NOT NULL DEFAULT 0,
    text_count INTEGER NOT NULL DEFAULT 0,
    name_greek TEXT,
    description TEXT,
    data_source TEXT NOT NULL DEFAULT 'topostext'
);

-- Timeline markers table
CREATE TABLE IF NOT EXISTS timeline_markers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    marker_type TEXT NOT NULL DEFAULT 'minor'
);

-- Event participants junction table
CREATE TABLE IF NOT EXISTS event_participants (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    person_id TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'participant',
    side TEXT,
    UNIQUE(event_id, person_id)
);

-- Road cities junction table
CREATE TABLE IF NOT EXISTS road_cities (
    id TEXT PRIMARY KEY,
    road_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    sequence_order INTEGER,
    distance_from_start_km REAL,
    UNIQUE(road_id, location_id)
);

-- Person relationships junction table
CREATE TABLE IF NOT EXISTS person_relationships (
    id TEXT PRIMARY KEY,
    person1_id TEXT NOT NULL,
    person2_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    start_year INTEGER,
    end_year INTEGER,
    UNIQUE(person1_id, person2_id, relationship_type)
);

-- Person roles table
CREATE TABLE IF NOT EXISTS person_roles (
    id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL,
    role TEXT NOT NULL,
    start_year INTEGER,
    end_year INTEGER,
    location_id TEXT
);

-- Administrative divisions table
CREATE TABLE IF NOT EXISTS admin_divisions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_latin TEXT,
    division_type TEXT NOT NULL,
    parent_id TEXT,
    start_year INTEGER NOT NULL,
    end_year INTEGER,
    polygon_geojson TEXT,
    centroid_lat REAL,
    centroid_lon REAL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_locations_coords ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type);
CREATE INDEX IF NOT EXISTS idx_provinces_years ON provinces(start_year, end_year);
CREATE INDEX IF NOT EXISTS idx_roads_year ON roads(construction_year);
CREATE INDEX IF NOT EXISTS idx_people_years ON people(birth_year, death_year);
CREATE INDEX IF NOT EXISTS idx_events_year ON events(year);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_travel_network_source ON travel_network(source_location_id);
CREATE INDEX IF NOT EXISTS idx_travel_network_target ON travel_network(target_location_id);
CREATE INDEX IF NOT EXISTS idx_ancient_sources_location ON ancient_sources(location_id);

-- FTS5 search indexes (standalone, manually populated)
CREATE VIRTUAL TABLE IF NOT EXISTS location_search USING fts5(
    location_id,
    name_latin,
    name_modern,
    description
);

CREATE VIRTUAL TABLE IF NOT EXISTS people_search USING fts5(
    person_id,
    name,
    name_latin,
    description
);
"""

# Default timeline markers
DEFAULT_TIMELINE_MARKERS: list[tuple[int, str, str, str]] = [
    (-753, "Founding of Rome", "Traditional founding date of Rome by Romulus", "major"),
    (-509, "Roman Republic Founded", "Overthrow of monarchy, Republic established", "major"),
    (-264, "First Punic War Begins", "Rome vs Carthage for Mediterranean dominance", "minor"),
    (-218, "Second Punic War Begins", "Hannibal crosses the Alps", "major"),
    (-146, "Destruction of Carthage", "End of Punic Wars, Rome dominates Mediterranean", "major"),
    (-44, "Assassination of Caesar", "Death of Julius Caesar", "major"),
    (-31, "Battle of Actium", "Octavian defeats Antony and Cleopatra", "major"),
    (-27, "Augustus Becomes Emperor", "Beginning of the Roman Empire", "major"),
    (79, "Eruption of Vesuvius", "Destruction of Pompeii and Herculaneum", "major"),
    (117, "Peak of Empire", "Maximum territorial extent under Trajan", "major"),
    (284, "Diocletian's Reforms", "Beginning of the Dominate", "major"),
    (313, "Edict of Milan", "Christianity legalized", "major"),
    (330, "Constantinople Founded", "New eastern capital established", "major"),
    (395, "Division of Empire", "Permanent split into Western and Eastern empires", "major"),
    (410, "Sack of Rome", "Visigoths sack Rome under Alaric", "major"),
    (476, "Fall of Western Empire", "Deposition of Romulus Augustulus", "major"),
]

# Province colors for visualization
PROVINCE_COLORS: list[str] = [
    "#C4A484",  # Terracotta/tan
    "#D4A574",  # Warm sand
    "#B8956E",  # Ochre
    "#A08060",  # Brown
    "#C9B896",  # Beige
    "#D6C4A8",  # Cream
    "#BFA980",  # Golden brown
    "#A89070",  # Dusty brown
    "#C8B090",  # Light tan
    "#B09878",  # Medium tan
]
