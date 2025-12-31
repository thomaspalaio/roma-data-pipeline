"""
Main pipeline orchestrator for Roma Data Pipeline.

Coordinates the download, transform, enrich, and build stages.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from roma_data.config import Config

logger = logging.getLogger(__name__)
console = Console()


class Pipeline:
    """
    Main pipeline orchestrator.

    Example:
        >>> from roma_data import Pipeline, Config
        >>> config = Config(sources=["pleiades", "orbis"])
        >>> pipeline = Pipeline(config)
        >>> db_path = pipeline.run()
    """

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the pipeline.

        Args:
            config: Pipeline configuration. If None, uses defaults.
        """
        from roma_data.config import Config

        self.config = config or Config()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging based on verbosity."""
        level = logging.DEBUG if self.config.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def run(self) -> Path:
        """
        Run the full pipeline.

        Returns:
            Path to the generated SQLite database.
        """
        # Ensure directories exist
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.raw_dir.mkdir(parents=True, exist_ok=True)
        self.config.processed_dir.mkdir(parents=True, exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Stage 1: Download
            task = progress.add_task("Downloading data sources...", total=None)
            self._run_download()
            progress.update(task, completed=True)

            # Stage 2: Transform
            task = progress.add_task("Transforming data...", total=None)
            self._run_transform()
            progress.update(task, completed=True)

            # Stage 3: Enrich
            task = progress.add_task("Enriching with cross-links...", total=None)
            self._run_enrich()
            progress.update(task, completed=True)

            # Stage 4: Build database
            task = progress.add_task("Building SQLite database...", total=None)
            self._run_build()
            progress.update(task, completed=True)

            # Stage 5: Validate (optional)
            if self.config.validate_output:
                task = progress.add_task("Validating database...", total=None)
                self._run_validate()
                progress.update(task, completed=True)

            # Stage 6: Export additional formats (optional)
            if self.config.export_geojson or self.config.export_csv:
                task = progress.add_task("Exporting additional formats...", total=None)
                self._run_export()
                progress.update(task, completed=True)

        return self.config.output_path

    def _run_download(self) -> dict[str, int]:
        """Download all enabled data sources."""
        results: dict[str, int] = {}

        if "pleiades" in self.config.sources:
            from roma_data.sources.pleiades import PleiadesSource
            source = PleiadesSource(self.config)
            results["pleiades"] = source.download()

        if "awmc" in self.config.sources:
            from roma_data.sources.awmc import AWMCSource
            source = AWMCSource(self.config)
            results["awmc"] = source.download()

        if "itinere" in self.config.sources:
            from roma_data.sources.itinere import ItinereSource
            source = ItinereSource(self.config)
            results["itinere"] = source.download()

        if "wikidata" in self.config.sources:
            from roma_data.sources.wikidata import WikidataSource
            source = WikidataSource(self.config)
            results["wikidata"] = source.download()

        if "orbis" in self.config.sources:
            from roma_data.sources.orbis import ORBISSource
            source = ORBISSource(self.config)
            results["orbis"] = source.download()

        if "topostext" in self.config.sources:
            from roma_data.sources.topostext import ToposTextSource
            source = ToposTextSource(self.config)
            results["topostext"] = source.download()

        logger.info(f"Downloaded: {results}")
        return results

    def _run_transform(self) -> dict[str, int]:
        """Transform raw data to processed format."""
        results: dict[str, int] = {}

        from roma_data.transform.locations import transform_locations
        from roma_data.transform.provinces import transform_provinces
        from roma_data.transform.roads import transform_roads
        from roma_data.transform.people import transform_people
        from roma_data.transform.events import transform_events

        results["locations"] = transform_locations(self.config)
        results["provinces"] = transform_provinces(self.config)
        results["roads"] = transform_roads(self.config)
        results["people"] = transform_people(self.config)
        results["events"] = transform_events(self.config)

        logger.info(f"Transformed: {results}")
        return results

    def _run_enrich(self) -> None:
        """Enrich data with cross-entity links."""
        from roma_data.transform.enrichment import enrich_all
        enrich_all(self.config)

    def _run_build(self) -> Path:
        """Build the SQLite database."""
        from roma_data.export.sqlite import SQLiteExporter
        exporter = SQLiteExporter(self.config)
        return exporter.export()

    def _run_validate(self) -> dict[str, bool]:
        """Validate the generated database."""
        from roma_data.validation.checks import validate_database
        return validate_database(self.config.output_path, verbose=self.config.verbose)

    def _run_export(self) -> None:
        """Export to additional formats."""
        if self.config.export_geojson:
            from roma_data.export.geojson import export_all_geojson
            export_all_geojson(self.config)

        if self.config.export_csv:
            from roma_data.export.csv import export_all_csv
            export_all_csv(self.config)

    # Individual stage methods for partial runs

    def download_only(self) -> dict[str, int]:
        """Run only the download stage."""
        self.config.raw_dir.mkdir(parents=True, exist_ok=True)
        return self._run_download()

    def transform_only(self) -> dict[str, int]:
        """Run only the transform stage."""
        self.config.processed_dir.mkdir(parents=True, exist_ok=True)
        return self._run_transform()

    def build_only(self) -> dict[str, int]:
        """Run only the database build stage."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        return self._run_build()

    def validate_only(self) -> dict[str, bool]:
        """Run only validation."""
        return self._run_validate()
