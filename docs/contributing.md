# Contributing

Guide for contributing to Roma Data Pipeline.

## Ways to Contribute

- **Bug Reports**: Found a bug? Open an issue
- **Feature Requests**: Suggest new features
- **Data Sources**: Propose new data sources
- **Documentation**: Improve docs
- **Code**: Fix bugs or add features

## Development Setup

### Prerequisites

- Python 3.10+
- Git

### Clone and Install

```bash
# Clone repository
git clone https://github.com/romadatapipeline/roma-data-pipeline.git
cd roma-data-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=roma_data --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check src/

# Type checking
mypy src/roma_data

# Format code
ruff format src/
```

## Adding a New Data Source

### 1. Create Source Module

Create `src/roma_data/sources/newsource.py`:

```python
from roma_data.sources.base import DataSource

class NewSource(DataSource):
    name = "newsource"
    description = "Description of new source"

    def download(self) -> int:
        """Download raw data."""
        # Implement download logic
        return record_count

    def transform(self) -> list:
        """Transform to standard format."""
        # Return list of location dicts
        return locations
```

### 2. Register Source

Add to `src/roma_data/constants.py`:

```python
AVAILABLE_SOURCES = [
    "pleiades",
    "orbis",
    # ...
    "newsource",  # Add here
]
```

### 3. Add Constants

Add URLs and mappings to `constants.py`:

```python
NEWSOURCE_URL = "https://example.com/data.json"
```

### 4. Write Tests

Create `tests/test_sources/test_newsource.py`:

```python
import pytest
from roma_data.sources.newsource import NewSource

def test_transform():
    # Test transformation logic
    pass
```

### 5. Document

Update `docs/data-sources.md` with:

- Source description
- License information
- Data provided
- Attribution requirements

## Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** and add tests
4. **Run checks**: `pytest && ruff check src/`
5. **Commit**: Use descriptive commit messages
6. **Push**: `git push origin feature/my-feature`
7. **Open PR**: Describe your changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add ToposText citation extraction

- Parse "X in Y texts" format
- Extract reference counts
- Add to location records
```

### PR Requirements

- [ ] Tests pass
- [ ] Code is linted
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG updated (for features)

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small

### Example Function

```python
def transform_location(raw: dict) -> dict:
    """
    Transform raw location data to standard format.

    Args:
        raw: Raw location dictionary from source.

    Returns:
        Standardized location dictionary.

    Raises:
        ValueError: If required fields are missing.
    """
    if "name" not in raw:
        raise ValueError("Missing required field: name")

    return {
        "id": f"source_{raw['id']}",
        "name_latin": raw["name"],
        "latitude": raw.get("lat"),
        "longitude": raw.get("lon"),
    }
```

## Data Source Requirements

Before proposing a new data source:

1. **License**: Must be open data (CC-BY, CC0, or similar)
2. **Quality**: Academically credible source
3. **Format**: Machine-readable (JSON, CSV, GeoJSON, API)
4. **Value**: Provides unique data not in existing sources

## Questions?

- Open a GitHub Discussion for questions
- Check existing issues before opening new ones
