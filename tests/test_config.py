"""Tests for configuration module."""

from __future__ import annotations

from pathlib import Path

import pytest

from roma_data.config import ALL_SOURCES, Config


def test_config_defaults() -> None:
    """Test default configuration values."""
    config = Config()

    assert config.output_name == "roma_aeterna.sqlite"
    assert config.sources == ALL_SOURCES
    assert config.time_range is None
    assert config.bbox is None
    assert config.include_images is False


def test_config_custom_sources() -> None:
    """Test configuration with custom sources."""
    config = Config(sources=frozenset({"pleiades", "orbis"}))

    assert config.sources == {"pleiades", "orbis"}


def test_config_invalid_source() -> None:
    """Test that invalid sources raise ValueError."""
    with pytest.raises(ValueError, match="Invalid data sources"):
        Config(sources=frozenset({"invalid_source"}))


def test_config_time_range() -> None:
    """Test time range configuration."""
    config = Config(time_range=(-200, 200))

    assert config.time_range == (-200, 200)


def test_config_invalid_time_range() -> None:
    """Test that invalid time range raises ValueError."""
    with pytest.raises(ValueError, match="Invalid time range"):
        Config(time_range=(200, -200))  # start > end


def test_config_bbox() -> None:
    """Test bounding box configuration."""
    config = Config(bbox=(-10.0, 35.0, 20.0, 50.0))

    assert config.bbox == (-10.0, 35.0, 20.0, 50.0)


def test_config_output_path() -> None:
    """Test output_path property."""
    config = Config(output_dir=Path("/tmp"), output_name="test.sqlite")

    assert config.output_path == Path("/tmp/test.sqlite")


def test_config_with_sources() -> None:
    """Test with_sources method."""
    config = Config()
    new_config = config.with_sources(["pleiades"])

    assert config.sources == ALL_SOURCES  # Original unchanged
    assert new_config.sources == {"pleiades"}


def test_config_with_output() -> None:
    """Test with_output method."""
    config = Config()
    new_config = config.with_output("/tmp/custom.sqlite")

    assert new_config.output_dir == Path("/tmp")
    assert new_config.output_name == "custom.sqlite"
