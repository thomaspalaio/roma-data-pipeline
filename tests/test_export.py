"""Tests for export functionality."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def sample_database(tmp_path: Path) -> Path:
    """Create a sample database for testing exports."""
    db_path = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db_path)

    # Create tables
    conn.executescript("""
        CREATE TABLE locations (
            id TEXT PRIMARY KEY,
            name_latin TEXT NOT NULL,
            name_modern TEXT,
            type TEXT NOT NULL DEFAULT 'other',
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            description TEXT,
            founding_year INTEGER,
            destruction_year INTEGER,
            peak_population INTEGER,
            province_id TEXT,
            parent_location_id TEXT,
            thumbnail_filename TEXT,
            confidence TEXT NOT NULL DEFAULT 'probable',
            pleiades_uri TEXT,
            wikidata_id TEXT,
            ancient_text_refs INTEGER,
            ancient_text_count INTEGER,
            topostext_url TEXT
        );

        CREATE TABLE provinces (
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

        CREATE TABLE roads (
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
    """)

    # Insert sample data
    conn.execute("""
        INSERT INTO locations (id, name_latin, name_modern, type, latitude, longitude, confidence)
        VALUES ('test_1', 'Roma', 'Rome', 'city', 41.8919, 12.4853, 'certain')
    """)

    conn.execute("""
        INSERT INTO locations (id, name_latin, name_modern, type, latitude, longitude, confidence)
        VALUES ('test_2', 'Pompeii', 'Pompei', 'city', 40.7509, 14.4869, 'certain')
    """)

    conn.execute("""
        INSERT INTO provinces (id, name, name_latin, start_year, polygon_geojson, centroid_lat, centroid_lon)
        VALUES ('italia', 'Italia', 'Italia', -509, '{"type":"Polygon","coordinates":[[[12,41],[13,41],[13,42],[12,42],[12,41]]]}', 41.5, 12.5)
    """)

    conn.execute("""
        INSERT INTO roads (id, name, name_latin, path_geojson, road_type, length_km)
        VALUES ('via_appia', 'Via Appia', 'Via Appia', '{"type":"LineString","coordinates":[[12.4853,41.8919],[14.4869,40.7509]]}', 'major', 230.5)
    """)

    conn.commit()
    conn.close()

    return db_path


class TestGeoJSONExport:
    """Tests for GeoJSON export."""

    def test_export_locations(self, sample_database: Path, tmp_path: Path):
        """Test exporting locations to GeoJSON."""
        from roma_data.export.geojson import export_geojson

        output = tmp_path / "locations.geojson"
        count = export_geojson(sample_database, "locations", output)

        assert count == 2
        assert output.exists()

        with open(output) as f:
            data = json.load(f)

        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2
        assert data["features"][0]["geometry"]["type"] == "Point"

    def test_export_provinces(self, sample_database: Path, tmp_path: Path):
        """Test exporting provinces to GeoJSON."""
        from roma_data.export.geojson import export_geojson

        output = tmp_path / "provinces.geojson"
        count = export_geojson(sample_database, "provinces", output)

        assert count == 1
        assert output.exists()

        with open(output) as f:
            data = json.load(f)

        assert data["features"][0]["geometry"]["type"] == "Polygon"

    def test_export_roads(self, sample_database: Path, tmp_path: Path):
        """Test exporting roads to GeoJSON."""
        from roma_data.export.geojson import export_geojson

        output = tmp_path / "roads.geojson"
        count = export_geojson(sample_database, "roads", output)

        assert count == 1

        with open(output) as f:
            data = json.load(f)

        assert data["features"][0]["geometry"]["type"] == "LineString"

    def test_export_invalid_table(self, sample_database: Path, tmp_path: Path):
        """Test that invalid table raises ValueError."""
        from roma_data.export.geojson import export_geojson

        output = tmp_path / "invalid.geojson"

        with pytest.raises(ValueError, match="Unknown table"):
            export_geojson(sample_database, "invalid_table", output)


class TestCSVExport:
    """Tests for CSV export."""

    def test_export_locations_csv(self, sample_database: Path, tmp_path: Path):
        """Test exporting locations to CSV."""
        from roma_data.export.csv import export_csv

        output = tmp_path / "locations.csv"
        count = export_csv(sample_database, "locations", output)

        assert count == 2
        assert output.exists()

        # Check CSV content
        content = output.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3  # Header + 2 rows
        assert "name_latin" in lines[0]
        assert "Roma" in lines[1]

    def test_export_provinces_csv(self, sample_database: Path, tmp_path: Path):
        """Test exporting provinces to CSV."""
        from roma_data.export.csv import export_csv

        output = tmp_path / "provinces.csv"
        count = export_csv(sample_database, "provinces", output)

        assert count == 1

    def test_export_roads_csv(self, sample_database: Path, tmp_path: Path):
        """Test exporting roads to CSV."""
        from roma_data.export.csv import export_csv

        output = tmp_path / "roads.csv"
        count = export_csv(sample_database, "roads", output)

        assert count == 1
        content = output.read_text()
        assert "Via Appia" in content
