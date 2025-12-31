"""Pytest configuration and fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from roma_data.config import Config


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def test_config(temp_output_dir: Path) -> Config:
    """Test configuration with temporary output directory."""
    return Config(
        output_dir=temp_output_dir,
        sources=frozenset({"pleiades"}),  # Minimal source for fast tests
        cache_downloads=False,
    )
