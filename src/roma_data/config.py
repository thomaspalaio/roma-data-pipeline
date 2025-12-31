"""
Configuration management for Roma Data Pipeline.

Provides a dataclass-based configuration system that can be customized
programmatically or loaded from files/environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# All available data sources
ALL_SOURCES = frozenset({
    "pleiades",
    "awmc",
    "itinere",
    "wikidata",
    "orbis",
    "topostext",
})


@dataclass
class Config:
    """
    Pipeline configuration with sensible defaults.

    Attributes:
        output_dir: Directory for output files (default: ./output)
        output_name: Name of the SQLite database (default: roma_aeterna.sqlite)
        sources: List of data sources to include (default: all)
        time_range: Optional (start_year, end_year) filter
        bbox: Optional bounding box (min_lon, min_lat, max_lon, max_lat)
        location_types: Optional list of location types to include
        include_images: Whether to download location images
        max_images: Maximum number of images to download
        request_delay: Delay between HTTP requests (for rate limiting)
        cache_downloads: Whether to cache downloaded files
        export_geojson: Also export GeoJSON files
        export_csv: Also export CSV files
        validate_output: Run validation after build
        verbose: Enable verbose logging
    """

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    output_name: str = "roma_aeterna.sqlite"

    # Data sources to include (all by default)
    sources: frozenset[str] = field(default_factory=lambda: ALL_SOURCES)

    # Filtering options
    time_range: tuple[int, int] | None = None  # (start_year, end_year)
    bbox: tuple[float, float, float, float] | None = None  # (min_lon, min_lat, max_lon, max_lat)
    location_types: frozenset[str] | None = None

    # Image download settings
    include_images: bool = False
    max_images: int = 100

    # Network settings
    request_delay: float = 1.0  # seconds between requests
    cache_downloads: bool = True

    # Export formats
    export_geojson: bool = False
    export_csv: bool = False

    # Validation
    validate_output: bool = True

    # Logging
    verbose: bool = False

    @property
    def output_path(self) -> Path:
        """Full path to the output database."""
        return self.output_dir / self.output_name

    @property
    def raw_dir(self) -> Path:
        """Directory for raw downloaded data."""
        return self.output_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        """Directory for processed intermediate data."""
        return self.output_dir / "processed"

    def __post_init__(self) -> None:
        """Validate and normalize configuration."""
        # Convert sources to frozenset if needed
        if isinstance(self.sources, (list, tuple, set)):
            self.sources = frozenset(self.sources)

        # Validate sources
        invalid = self.sources - ALL_SOURCES
        if invalid:
            raise ValueError(f"Invalid data sources: {invalid}. Valid: {ALL_SOURCES}")

        # Convert location_types to frozenset if needed
        if self.location_types is not None and not isinstance(self.location_types, frozenset):
            self.location_types = frozenset(self.location_types)

        # Convert output_dir to Path if string
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Validate time range
        if self.time_range is not None:
            start, end = self.time_range
            if start > end:
                raise ValueError(f"Invalid time range: start ({start}) > end ({end})")

        # Validate bbox
        if self.bbox is not None:
            min_lon, min_lat, max_lon, max_lat = self.bbox
            if min_lon > max_lon:
                raise ValueError(f"Invalid bbox: min_lon ({min_lon}) > max_lon ({max_lon})")
            if min_lat > max_lat:
                raise ValueError(f"Invalid bbox: min_lat ({min_lat}) > max_lat ({max_lat})")

    @classmethod
    def from_env(cls) -> Config:
        """
        Load configuration from environment variables.

        Environment variables:
            ROMA_OUTPUT_DIR: Output directory
            ROMA_OUTPUT_NAME: Database filename
            ROMA_SOURCES: Comma-separated list of sources
            ROMA_TIME_START: Start year filter
            ROMA_TIME_END: End year filter
            ROMA_VERBOSE: Enable verbose logging (1/true/yes)
        """
        kwargs: dict[str, object] = {}

        if output_dir := os.environ.get("ROMA_OUTPUT_DIR"):
            kwargs["output_dir"] = Path(output_dir)

        if output_name := os.environ.get("ROMA_OUTPUT_NAME"):
            kwargs["output_name"] = output_name

        if sources := os.environ.get("ROMA_SOURCES"):
            kwargs["sources"] = frozenset(s.strip() for s in sources.split(","))

        time_start = os.environ.get("ROMA_TIME_START")
        time_end = os.environ.get("ROMA_TIME_END")
        if time_start and time_end:
            kwargs["time_range"] = (int(time_start), int(time_end))

        if verbose := os.environ.get("ROMA_VERBOSE"):
            kwargs["verbose"] = verbose.lower() in ("1", "true", "yes")

        return cls(**kwargs)

    def with_sources(self, sources: Sequence[str]) -> Config:
        """Return a new config with different sources."""
        return Config(
            output_dir=self.output_dir,
            output_name=self.output_name,
            sources=frozenset(sources),
            time_range=self.time_range,
            bbox=self.bbox,
            location_types=self.location_types,
            include_images=self.include_images,
            max_images=self.max_images,
            request_delay=self.request_delay,
            cache_downloads=self.cache_downloads,
            export_geojson=self.export_geojson,
            export_csv=self.export_csv,
            validate_output=self.validate_output,
            verbose=self.verbose,
        )

    def with_output(self, output_path: str | Path) -> Config:
        """Return a new config with different output path."""
        path = Path(output_path)
        return Config(
            output_dir=path.parent,
            output_name=path.name,
            sources=self.sources,
            time_range=self.time_range,
            bbox=self.bbox,
            location_types=self.location_types,
            include_images=self.include_images,
            max_images=self.max_images,
            request_delay=self.request_delay,
            cache_downloads=self.cache_downloads,
            export_geojson=self.export_geojson,
            export_csv=self.export_csv,
            validate_output=self.validate_output,
            verbose=self.verbose,
        )
