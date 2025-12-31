# Contributing to Roma Data Pipeline

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Report bugs**: Open an issue describing the bug and how to reproduce it
- **Suggest features**: Open an issue describing the feature and its use case
- **Add data sources**: Implement new data source integrations
- **Improve documentation**: Fix typos, add examples, clarify explanations
- **Write tests**: Increase test coverage

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/romadatapipeline/roma-data-pipeline
   cd roma-data-pipeline
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

- We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Type hints are required for all public functions
- Docstrings follow Google style

Run checks locally:
```bash
ruff check src/
ruff format src/
mypy src/
```

## Testing

Run tests with pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=roma_data --cov-report=html
```

## Adding a New Data Source

1. Create a new module in `src/roma_data/sources/`:
   ```python
   # src/roma_data/sources/newsource.py
   from roma_data.sources.base import DataSource

   class NewSource(DataSource):
       name = "newsource"
       description = "Description of the source"

       def download(self) -> int:
           # Download data from the source
           ...

       def transform(self) -> list[dict]:
           # Transform to common format
           ...
   ```

2. Add any URLs or constants to `src/roma_data/constants.py`

3. Register the source in `src/roma_data/config.py` (add to `ALL_SOURCES`)

4. Update the Pipeline in `src/roma_data/pipeline.py`

5. Add tests in `tests/test_sources/test_newsource.py`

6. Update documentation

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes with tests and documentation
3. Ensure all tests pass and linting is clean
4. Update CHANGELOG.md if appropriate
5. Submit a pull request with a clear description

## Data Source Requirements

When adding new data sources:

- **License**: Must be compatible with CC-BY or more permissive
- **Attribution**: Document the source and license in LICENSE-DATA
- **Quality**: Include validation checks for the data
- **Documentation**: Describe what data is provided and its limitations

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/). Please be respectful and constructive in all interactions.

## Questions?

Open an issue or reach out to the maintainers.
