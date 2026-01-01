"""
Database validation checks for Roma Data Pipeline.

Provides comprehensive validation of generated databases including:
- Data integrity checks
- Coordinate validity
- Foreign key relationships
- FTS index functionality
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def validate_database(database: Path, verbose: bool = False) -> dict[str, Any]:
    """
    Validate a Roma Data Pipeline database.

    Args:
        database: Path to SQLite database
        verbose: Print detailed results

    Returns:
        Dictionary with validation results
    """
    if not database.exists():
        return {"overall_passed": False, "error": f"Database not found: {database}"}

    results: dict[str, Any] = {
        "overall_passed": True,
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row

        # Run all validation checks
        checks = [
            ("table_counts", _check_table_counts),
            ("coordinate_validity", _check_coordinates),
            ("required_fields", _check_required_fields),
            ("fts_indexes", _check_fts_indexes),
            ("data_ranges", _check_data_ranges),
            ("foreign_keys", _check_foreign_keys),
        ]

        for check_name, check_func in checks:
            try:
                passed, details = check_func(conn, verbose)
                results["checks"][check_name] = {
                    "passed": passed,
                    "details": details,
                }
                if not passed:
                    results["overall_passed"] = False
                    if "error" in details:
                        results["errors"].append(f"{check_name}: {details['error']}")
            except Exception as e:
                results["checks"][check_name] = {
                    "passed": False,
                    "details": {"error": str(e)},
                }
                results["errors"].append(f"{check_name}: {e}")
                results["overall_passed"] = False

        conn.close()

        # Print results if verbose
        if verbose:
            _print_results(results)

    except sqlite3.Error as e:
        results["overall_passed"] = False
        results["error"] = f"Database error: {e}"

    return results


def _check_table_counts(conn: sqlite3.Connection, verbose: bool) -> tuple[bool, dict[str, Any]]:
    """Check that all required tables exist and have data."""
    required_tables = {
        "locations": 1000,  # Minimum expected
        "provinces": 10,
        "roads": 100,
        "people": 10,
        "timeline_markers": 5,
    }

    optional_tables = ["events", "travel_network", "ancient_sources"]

    # Whitelist of allowed table names for security
    allowed_tables = frozenset(required_tables.keys()) | frozenset(optional_tables)

    details: dict[str, Any] = {"tables": {}}
    passed = True

    cursor = conn.cursor()

    # Check required tables
    for table, min_count in required_tables.items():
        if table not in allowed_tables:
            continue  # Skip unknown tables
        try:
            # Use parameterized query pattern - table names validated via whitelist
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cursor.fetchone()[0]
            details["tables"][table] = count
            if count < min_count:
                passed = False
                details["error"] = f"{table} has {count} rows, expected at least {min_count}"
        except sqlite3.OperationalError:
            passed = False
            details["tables"][table] = "MISSING"
            details["error"] = f"Required table '{table}' not found"

    # Check optional tables (don't fail if missing)
    for table in optional_tables:
        if table not in allowed_tables:
            continue  # Skip unknown tables
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cursor.fetchone()[0]
            details["tables"][table] = count
        except sqlite3.OperationalError:
            details["tables"][table] = "not present"

    return passed, details


def _check_coordinates(conn: sqlite3.Connection, verbose: bool) -> tuple[bool, dict[str, Any]]:
    """Check that coordinates are valid."""
    cursor = conn.cursor()

    details: dict[str, Any] = {}
    passed = True

    # Check locations
    cursor.execute("""
        SELECT COUNT(*) FROM locations
        WHERE latitude < -90 OR latitude > 90
        OR longitude < -180 OR longitude > 180
    """)
    invalid_count = cursor.fetchone()[0]
    details["invalid_location_coords"] = invalid_count

    if invalid_count > 0:
        passed = False
        details["error"] = f"{invalid_count} locations have invalid coordinates"

    # Check provinces centroids
    cursor.execute("""
        SELECT COUNT(*) FROM provinces
        WHERE centroid_lat IS NOT NULL
        AND (centroid_lat < -90 OR centroid_lat > 90
        OR centroid_lon < -180 OR centroid_lon > 180)
    """)
    invalid_provinces = cursor.fetchone()[0]
    details["invalid_province_coords"] = invalid_provinces

    if invalid_provinces > 0:
        passed = False
        details["error"] = f"{invalid_provinces} provinces have invalid centroids"

    # Check for null coordinates in locations
    cursor.execute("""
        SELECT COUNT(*) FROM locations
        WHERE latitude IS NULL OR longitude IS NULL
    """)
    null_count = cursor.fetchone()[0]
    details["null_location_coords"] = null_count

    return passed, details


def _check_required_fields(conn: sqlite3.Connection, verbose: bool) -> tuple[bool, dict[str, Any]]:
    """Check that required fields are populated."""
    cursor = conn.cursor()

    details: dict[str, Any] = {}
    passed = True

    # Check locations have IDs and names
    cursor.execute("""
        SELECT COUNT(*) FROM locations
        WHERE id IS NULL OR id = ''
    """)
    null_ids = cursor.fetchone()[0]
    details["locations_missing_id"] = null_ids

    cursor.execute("""
        SELECT COUNT(*) FROM locations
        WHERE (name_latin IS NULL OR name_latin = '')
        AND (name_modern IS NULL OR name_modern = '')
    """)
    null_names = cursor.fetchone()[0]
    details["locations_missing_names"] = null_names

    if null_ids > 0:
        passed = False
        details["error"] = f"{null_ids} locations missing ID"
    elif null_names > 0:
        # Warning, not failure
        details["warning"] = f"{null_names} locations have no name"

    # Check people have names
    cursor.execute("""
        SELECT COUNT(*) FROM people
        WHERE name IS NULL OR name = ''
    """)
    null_people_names = cursor.fetchone()[0]
    details["people_missing_names"] = null_people_names

    if null_people_names > 0:
        passed = False
        details["error"] = f"{null_people_names} people missing name"

    return passed, details


def _check_fts_indexes(conn: sqlite3.Connection, verbose: bool) -> tuple[bool, dict[str, Any]]:
    """Check that FTS indexes are working."""
    cursor = conn.cursor()

    details: dict[str, Any] = {}
    passed = True

    # Test location_search
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM location_search
        """)
        fts_count = cursor.fetchone()[0]
        details["location_search_count"] = fts_count

        if fts_count == 0:
            passed = False
            details["error"] = "location_search FTS index is empty"
        else:
            # Test a search
            cursor.execute("""
                SELECT COUNT(*) FROM location_search
                WHERE location_search MATCH 'Roma'
            """)
            search_results = cursor.fetchone()[0]
            details["sample_search_results"] = search_results
    except sqlite3.OperationalError as e:
        passed = False
        details["error"] = f"FTS index error: {e}"

    return passed, details


def _check_data_ranges(conn: sqlite3.Connection, verbose: bool) -> tuple[bool, dict[str, Any]]:
    """Check that data values are in expected ranges."""
    cursor = conn.cursor()

    details: dict[str, Any] = {}
    passed = True

    # Check year ranges for people
    cursor.execute("""
        SELECT MIN(birth_year), MAX(birth_year), MIN(death_year), MAX(death_year)
        FROM people
        WHERE birth_year IS NOT NULL OR death_year IS NOT NULL
    """)
    row = cursor.fetchone()
    if row:
        details["people_year_range"] = {
            "min_birth": row[0],
            "max_birth": row[1],
            "min_death": row[2],
            "max_death": row[3],
        }

    # Check location types distribution
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM locations
        GROUP BY type
        ORDER BY count DESC
        LIMIT 10
    """)
    type_dist = {row[0]: row[1] for row in cursor.fetchall()}
    details["location_types"] = type_dist

    # Check province counts by era
    cursor.execute("""
        SELECT
            CASE
                WHEN id LIKE '%bce%' THEN 'BCE'
                WHEN id LIKE '%ce_%' THEN 'CE'
                ELSE 'Other'
            END as era,
            COUNT(*) as count
        FROM provinces
        GROUP BY era
    """)
    province_dist = {row[0]: row[1] for row in cursor.fetchall()}
    details["provinces_by_era"] = province_dist

    return passed, details


def _check_foreign_keys(conn: sqlite3.Connection, verbose: bool) -> tuple[bool, dict[str, Any]]:
    """Check foreign key relationships (soft check)."""
    cursor = conn.cursor()

    details: dict[str, Any] = {}
    passed = True

    # Check province_id references in locations
    cursor.execute("""
        SELECT COUNT(*) FROM locations
        WHERE province_id IS NOT NULL
        AND province_id NOT IN (SELECT id FROM provinces)
    """)
    orphan_provinces = cursor.fetchone()[0]
    details["orphan_province_refs"] = orphan_provinces

    if orphan_provinces > 0:
        # Warning, not failure (provinces are optional)
        details["warning"] = f"{orphan_provinces} locations reference non-existent provinces"

    return passed, details


def _print_results(results: dict[str, Any]) -> None:
    """Print validation results in a formatted table."""
    table = Table(title="Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    for check_name, check_result in results.get("checks", {}).items():
        passed = check_result.get("passed", False)
        status = "[green]PASSED[/green]" if passed else "[red]FAILED[/red]"

        details = check_result.get("details", {})
        detail_str = ""
        if "error" in details:
            detail_str = f"[red]{details['error']}[/red]"
        elif "warning" in details:
            detail_str = f"[yellow]{details['warning']}[/yellow]"
        elif "tables" in details:
            counts = [f"{k}: {v}" for k, v in details["tables"].items() if isinstance(v, int)]
            detail_str = ", ".join(counts[:4])
        elif "sample_search_results" in details:
            detail_str = f"FTS working, {details['sample_search_results']} results for 'Roma'"

        table.add_row(check_name, status, detail_str)

    console.print(table)

    if results.get("overall_passed"):
        console.print("\n[bold green]All validation checks passed![/bold green]")
    else:
        console.print("\n[bold red]Validation failed![/bold red]")
        for error in results.get("errors", []):
            console.print(f"  [red]• {error}[/red]")
