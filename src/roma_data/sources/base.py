"""
Base class for data sources.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from roma_data.config import Config


class DataSource(ABC):
    """
    Abstract base class for data sources.

    All data source implementations should inherit from this class
    and implement the required methods.
    """

    name: str = "base"
    description: str = "Base data source"

    def __init__(self, config: Config) -> None:
        """
        Initialize the data source.

        Args:
            config: Pipeline configuration.
        """
        self.config = config

    @property
    def raw_dir(self) -> Path:
        """Directory for raw downloaded data."""
        return self.config.raw_dir / self.name

    @property
    def processed_dir(self) -> Path:
        """Directory for processed data."""
        return self.config.processed_dir

    @abstractmethod
    def download(self) -> int:
        """
        Download data from the source.

        Returns:
            Number of records downloaded.
        """
        ...

    @abstractmethod
    def transform(self) -> list[dict[str, Any]]:
        """
        Transform raw data to processed format.

        Returns:
            List of transformed records.
        """
        ...

    def ensure_dirs(self) -> None:
        """Ensure required directories exist."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
