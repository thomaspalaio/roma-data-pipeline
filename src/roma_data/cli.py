"""
Command-line interface for Roma Data Pipeline.

Usage:
    roma-data run                              # Run full pipeline
    roma-data run --output ./my_db.sqlite      # Custom output path
    roma-data run --sources pleiades,orbis     # Subset of sources
    roma-data validate ./roma_aeterna.sqlite   # Validate database
    roma-data info                             # Show data source info
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
from rich.console import Console
from rich.table import Table

from roma_data import __version__
from roma_data.config import ALL_SOURCES, Config

if TYPE_CHECKING:
    pass

console = Console()


def parse_sources(ctx: click.Context, param: click.Parameter, value: str | None) -> frozenset[str]:
    """Parse comma-separated source list."""
    if value is None:
        return ALL_SOURCES
    sources = frozenset(s.strip().lower() for s in value.split(","))
    invalid = sources - ALL_SOURCES
    if invalid:
        raise click.BadParameter(f"Invalid sources: {invalid}. Valid: {', '.join(sorted(ALL_SOURCES))}")
    return sources


def parse_bbox(ctx: click.Context, param: click.Parameter, value: str | None) -> tuple[float, ...] | None:
    """Parse bounding box string (min_lon,min_lat,max_lon,max_lat)."""
    if value is None:
        return None
    try:
        parts = [float(x.strip()) for x in value.split(",")]
        if len(parts) != 4:
            raise ValueError("Expected 4 values")
        return tuple(parts)
    except ValueError as e:
        raise click.BadParameter(f"Invalid bbox format: {e}. Expected: min_lon,min_lat,max_lon,max_lat") from e


@click.group()
@click.version_option(version=__version__, prog_name="roma-data")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """
    Roma Data Pipeline - Comprehensive Roman World Dataset Generator

    Generate a unified SQLite database containing 28,500+ locations, 16,500+ roads,
    1,000+ historical figures, and pre-computed travel times across the Roman Empire.

    Data sources: Pleiades, AWMC, Itiner-e, Wikidata, ORBIS, ToposText
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@main.command()
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=Path("./roma_aeterna.sqlite"),
    help="Output database path",
)
@click.option(
    "-s", "--sources",
    callback=parse_sources,
    help=f"Comma-separated sources to include. Available: {', '.join(sorted(ALL_SOURCES))}",
)
@click.option(
    "--start-year",
    type=int,
    help="Filter: minimum year (e.g., -200 for 200 BCE)",
)
@click.option(
    "--end-year",
    type=int,
    help="Filter: maximum year (e.g., 200 for 200 CE)",
)
@click.option(
    "--bbox",
    callback=parse_bbox,
    help="Filter: bounding box as min_lon,min_lat,max_lon,max_lat",
)
@click.option(
    "--include-images/--no-images",
    default=False,
    help="Download location images from Wikimedia Commons",
)
@click.option(
    "--max-images",
    type=int,
    default=100,
    help="Maximum images to download (default: 100)",
)
@click.option(
    "--export-geojson/--no-geojson",
    default=False,
    help="Also export GeoJSON files",
)
@click.option(
    "--export-csv/--no-csv",
    default=False,
    help="Also export CSV files",
)
@click.option(
    "--skip-validation/--validate",
    default=False,
    help="Skip data validation after build",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without executing",
)
@click.pass_context
def run(
    ctx: click.Context,
    output: Path,
    sources: frozenset[str],
    start_year: int | None,
    end_year: int | None,
    bbox: tuple[float, ...] | None,
    include_images: bool,
    max_images: int,
    export_geojson: bool,
    export_csv: bool,
    skip_validation: bool,
    dry_run: bool,
) -> None:
    """
    Run the data pipeline to generate a Roman world database.

    Examples:

        roma-data run

        roma-data run --output ./custom.sqlite --sources pleiades,orbis

        roma-data run --start-year -200 --end-year 200 --bbox "-10,35,45,55"
    """
    verbose = ctx.obj.get("verbose", False)

    # Build time range tuple if both provided
    time_range = None
    if start_year is not None and end_year is not None:
        time_range = (start_year, end_year)
    elif start_year is not None:
        time_range = (start_year, 476)  # Default end: fall of Western Empire
    elif end_year is not None:
        time_range = (-753, end_year)  # Default start: founding of Rome

    # Create config
    config = Config(
        output_dir=output.parent,
        output_name=output.name,
        sources=sources,
        time_range=time_range,
        bbox=bbox,  # type: ignore[arg-type]
        include_images=include_images,
        max_images=max_images,
        export_geojson=export_geojson,
        export_csv=export_csv,
        validate_output=not skip_validation,
        verbose=verbose,
    )

    # Dry run: just show config
    if dry_run:
        console.print("\n[bold]Dry run - would execute with:[/bold]\n")
        _show_config(config)
        return

    # Show config
    if verbose:
        console.print("\n[bold]Configuration:[/bold]\n")
        _show_config(config)

    # Run pipeline
    console.print(f"\n[bold green]Starting Roma Data Pipeline v{__version__}[/bold green]\n")

    try:
        from roma_data.pipeline import Pipeline

        pipeline = Pipeline(config)
        db_path = pipeline.run()

        console.print("\n[bold green]Pipeline complete![/bold green]")
        console.print(f"Database: {db_path}")
        console.print(f"Size: {db_path.stat().st_size / (1024 * 1024):.2f} MB")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("database", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--strict", is_flag=True, help="Fail on warnings")
@click.pass_context
def validate(ctx: click.Context, database: Path, strict: bool) -> None:
    """
    Validate a Roma Data Pipeline database.

    Checks data integrity, coordinate validity, foreign key relationships,
    and FTS index functionality.
    """
    verbose = ctx.obj.get("verbose", False)

    console.print(f"\n[bold]Validating:[/bold] {database}\n")

    try:
        from roma_data.validation.checks import validate_database

        results = validate_database(database, verbose=verbose)

        if results.get("overall_passed"):
            console.print("\n[bold green]Validation PASSED[/bold green]")
        else:
            console.print("\n[bold red]Validation FAILED[/bold red]")
            if strict:
                sys.exit(1)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """
    Show information about available data sources.
    """
    table = Table(title="Roma Data Pipeline - Data Sources")
    table.add_column("Source", style="cyan")
    table.add_column("Description")
    table.add_column("License")
    table.add_column("Records", justify="right")

    sources = [
        ("pleiades", "Ancient place gazetteer", "CC-BY 3.0", "~28,500"),
        ("awmc", "Province boundaries (4 time periods)", "CC-BY 3.0", "~100"),
        ("itinere", "Roman road network", "Academic", "~16,500"),
        ("wikidata", "People, events, infrastructure", "CC0", "~2,000"),
        ("orbis", "Travel network (times/costs)", "CC-BY", "~600"),
        ("topostext", "Ancient text citations", "ODbL", "~3,000"),
    ]

    for name, desc, license_, records in sources:
        table.add_row(name, desc, license_, records)

    console.print()
    console.print(table)
    console.print()
    console.print("[dim]For more information, see: https://roma-data-pipeline.readthedocs.io[/dim]")


@main.command()
@click.argument("format", type=click.Choice(["geojson", "csv"]))
@click.argument("output", type=click.Path(dir_okay=False, writable=True, path_type=Path))
@click.option(
    "-d", "--database",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("./roma_aeterna.sqlite"),
    help="Source database path",
)
@click.option(
    "-t", "--table",
    type=click.Choice(["locations", "roads", "provinces", "people", "events"]),
    default="locations",
    help="Table to export",
)
@click.pass_context
def export(
    ctx: click.Context,
    format: str,
    output: Path,
    database: Path,
    table: str,
) -> None:
    """
    Export data from database to other formats.

    Examples:

        roma-data export geojson locations.geojson

        roma-data export csv roads.csv --table roads
    """
    verbose = ctx.obj.get("verbose", False)

    console.print(f"\nExporting {table} from {database} to {format}...")

    try:
        if format == "geojson":
            from roma_data.export.geojson import export_geojson
            export_geojson(database, table, output, verbose=verbose)
        elif format == "csv":
            from roma_data.export.csv import export_csv
            export_csv(database, table, output, verbose=verbose)

        console.print(f"[green]Exported to:[/green] {output}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


def _show_config(config: Config) -> None:
    """Display configuration in a table."""
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("Output", str(config.output_path))
    table.add_row("Sources", ", ".join(sorted(config.sources)))
    table.add_row("Time range", str(config.time_range) if config.time_range else "all")
    table.add_row("Bounding box", str(config.bbox) if config.bbox else "all")
    table.add_row("Include images", str(config.include_images))
    table.add_row("Export GeoJSON", str(config.export_geojson))
    table.add_row("Export CSV", str(config.export_csv))
    table.add_row("Validate", str(config.validate_output))

    console.print(table)


if __name__ == "__main__":
    main()
