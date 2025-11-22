# GEMINI.md

## Project Overview

`epydemics` is a Python library for epidemiological modeling and forecasting. It provides tools for creating, fitting, and evaluating discrete SIRD models with time-dependent parameters. The library is designed to be flexible and extensible, allowing users to easily incorporate their own data and models.

The main technologies used are Python, pandas for data manipulation, statsmodels for time series analysis, and matplotlib for plotting. The project is structured as a standard Python library with the source code in the `epydemics` directory and tests in the `tests` directory.

The core components are:
- **DataContainer**: For loading, preprocessing, and storing data.
- **Model**: The main class for creating and managing models.
- **SIRD Model**: A discrete Susceptible-Infected-Recovered-Deceased model.

## Building and Running

### Installation

You can install `epydemics` from PyPI:

```bash
pip install epydemics
```

To install the latest development version, you can clone this repository and install it in editable mode:

```bash
git clone https://github.com/julihocc/epydemics.git
cd epydemics
pip install -e .
```

### Running Tests

To run the tests, use `pytest`:

```bash
pytest
```

## Development Conventions

### Code Style

The project uses `black` for code formatting, `isort` for import sorting, and `flake8` for linting. There is a pre-commit configuration in `.pre-commit-config.yaml` to enforce these standards.

### Testing

The project uses `pytest` for testing. Tests are located in the `tests` directory and are organized into `unit` and `integration` tests.

### Contribution Guidelines

Contribution guidelines are available in `CONTRIBUTING.md`.
