"""Tests for validation functionality."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def valid_database(tmp_path: Path) -> Path:
    """Create a valid database for testing validation."""
    db_path = tmp_path / "valid.sqlite"
    conn = sqlite3.connect(db_path)

    # Create minimal schema
    conn.executescript("""
        CREATE TABLE locations (
            id TEXT PRIMARY KEY,
            name_latin TEXT NOT NULL,
            name_modern TEXT,
            type TEXT NOT NULL DEFAULT 'other',
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            confidence TEXT NOT NULL DEFAULT 'probable'
        );

        CREATE TABLE provinces (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            name_latin TEXT NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER,
            polygon_geojson TEXT NOT NULL,
            centroid_lat REAL,
            centroid_lon REAL
        );

        CREATE TABLE roads (
            id TEXT PRIMARY KEY,
            name TEXT,
            name_latin TEXT,
            path_geojson TEXT NOT NULL,
            road_type TEXT NOT NULL DEFAULT 'secondary',
            confidence TEXT NOT NULL DEFAULT 'probable'
        );

        CREATE TABLE people (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            birth_year INTEGER,
            death_year INTEGER
        );

        CREATE TABLE timeline_markers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            marker_type TEXT NOT NULL DEFAULT 'minor'
        );

        CREATE VIRTUAL TABLE location_search USING fts5(
            name_latin, name_modern, type, description,
            content='locations'
        );
    """)

    # Insert sample data (enough to pass validation)
    for i in range(1500):
        conn.execute("""
            INSERT INTO locations (id, name_latin, type, latitude, longitude, confidence)
            VALUES (?, ?, 'city', ?, ?, 'certain')
        """, (f"loc_{i}", f"City {i}", 40.0 + (i * 0.01), 12.0 + (i * 0.01)))

    for i in range(20):
        conn.execute("""
            INSERT INTO provinces (id, name, name_latin, start_year, polygon_geojson)
            VALUES (?, ?, ?, -100, '{}')
        """, (f"prov_{i}", f"Province {i}", f"Provincia {i}"))

    for i in range(200):
        conn.execute("""
            INSERT INTO roads (id, name, path_geojson)
            VALUES (?, ?, '{}')
        """, (f"road_{i}", f"Via {i}"))

    for i in range(20):
        conn.execute("""
            INSERT INTO people (id, name)
            VALUES (?, ?)
        """, (f"person_{i}", f"Person {i}"))

    for i in range(10):
        conn.execute("""
            INSERT INTO timeline_markers (year, name)
            VALUES (?, ?)
        """, (-500 + (i * 100), f"Event {i}"))

    # Populate FTS
    conn.execute("""
        INSERT INTO location_search(location_search)
        VALUES('rebuild')
    """)

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def invalid_database(tmp_path: Path) -> Path:
    """Create a database with validation issues."""
    db_path = tmp_path / "invalid.sqlite"
    conn = sqlite3.connect(db_path)

    conn.executescript("""
        CREATE TABLE locations (
            id TEXT PRIMARY KEY,
            name_latin TEXT,
            latitude REAL,
            longitude REAL
        );
    """)

    # Insert location with invalid coordinates
    conn.execute("""
        INSERT INTO locations (id, name_latin, latitude, longitude)
        VALUES ('bad_1', 'Bad Location', 200, 400)
    """)

    conn.commit()
    conn.close()

    return db_path


class TestValidation:
    """Tests for database validation."""

    def test_validate_valid_database(self, valid_database: Path):
        """Test validation passes for valid database."""
        from roma_data.validation.checks import validate_database

        results = validate_database(valid_database)

        assert results["overall_passed"] is True
        assert "table_counts" in results["checks"]
        assert results["checks"]["table_counts"]["passed"] is True

    def test_validate_missing_database(self, tmp_path: Path):
        """Test validation fails for missing database."""
        from roma_data.validation.checks import validate_database

        results = validate_database(tmp_path / "nonexistent.sqlite")

        assert results["overall_passed"] is False
        assert "error" in results

    def test_coordinate_validation(self, valid_database: Path):
        """Test coordinate validation check."""
        from roma_data.validation.checks import validate_database

        results = validate_database(valid_database)

        assert "coordinate_validity" in results["checks"]
        assert results["checks"]["coordinate_validity"]["passed"] is True

    def test_fts_validation(self, valid_database: Path):
        """Test FTS index validation."""
        from roma_data.validation.checks import validate_database

        results = validate_database(valid_database)

        assert "fts_indexes" in results["checks"]
        # FTS check should pass since we populated it
        assert results["checks"]["fts_indexes"]["passed"] is True
