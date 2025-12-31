"""
Roma Data Pipeline
==================

Comprehensive ETL pipeline for Roman world data from Pleiades, ORBIS, Wikidata, and more.

Example usage:

    >>> from roma_data import Pipeline, Config
    >>> pipeline = Pipeline()
    >>> db_path = pipeline.run()

Or from the command line:

    $ roma-data run
    $ roma-data run --output ./my_database.sqlite
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Thomas Palaio"

from roma_data.config import Config
from roma_data.pipeline import Pipeline

__all__ = [
    "__version__",
    "Config",
    "Pipeline",
]
