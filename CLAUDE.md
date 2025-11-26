# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Epydemics is a Python library for epidemiological modeling and forecasting that combines discrete SIRD (Susceptible-Infected-Recovered-Deaths) mathematical models with VAR (Vector Autoregression) time series analysis. Unlike classical epidemiological models with constant parameters, this project models time-varying infection, recovery, and mortality rates using logit-transformed rates.

**Key Innovation**: Rates (α, β, γ) are logit-transformed before VAR modeling to ensure they stay within (0,1) bounds, then inverse-transformed back for epidemic simulations.

## Development Workflow

### Git Worktree Setup
This project uses git worktrees for parallel development. The current worktree structure allows working on multiple branches simultaneously without switching:
```bash
# List all worktrees
git worktree list

# Create new worktree for a branch
git worktree add ../epydemics.worktrees/feature-name feature-branch-name

# Remove worktree when done
git worktree remove ../epydemics.worktrees/feature-name
```

### Version Management
- Current version: 0.6.1-dev (defined in `pyproject.toml`)
- Version also appears in `src/epydemics/__init__.py` as `__version__`
- Main branch: `main`
- When bumping versions, update both `pyproject.toml` and `src/epydemics/__init__.py`

## Development Commands

### Environment Setup
```bash
# Install package in editable mode with all dependencies
pip install -e .

# Install with development tools
pip install -e ".[dev,test]"

# Install with documentation tools
pip install -e ".[docs]"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests

# Run specific test file
pytest tests/test_model.py

# Run with coverage
pytest --cov=src/epydemics --cov-report=html

# Run in parallel
pytest -n auto
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

**Pre-commit Hooks**: This project uses extensive pre-commit hooks (configured in `.pre-commit-config.yaml`):
- Code formatting: `black` (line length 88)
- Import sorting: `isort` (black profile)
- Linting: `flake8`, `pylint`
- Type checking: `mypy`
- Security: `bandit`
- Documentation: `pydocstyle` (Google convention)
- Standard checks: trailing whitespace, EOF fixer, YAML/TOML/JSON validation, merge conflicts

**Important**: Pre-commit hooks will run automatically before each commit. If hooks fail, the commit will be rejected. Fix issues and retry.

### Documentation
```bash
# Build documentation (if docs directory exists)
cd docs && make html
```

## Architecture Overview

### Core Data Flow
```
Raw OWID Data → DataContainer → Feature Engineering → Model → Forecast → Simulation → Results
     ↓              ↓                  ↓                ↓          ↓          ↓
   CSV          Validation        SIRD Rates      VAR Model   Monte Carlo  Evaluation
              Smoothing         Logit Transform   Forecast    Scenarios    Visualization
```

### Module Structure

**`src/epydemics/core/`** - Core configuration and constants
- `config.py`: Settings management using pydantic-settings
- `constants.py`: Defines RATIOS, LOGIT_RATIOS, COMPARTMENTS, FORECASTING_LEVELS
- `exceptions.py`: Custom exceptions (NotDataFrameError, DataValidationError, DateRangeError)

**`src/epydemics/data/`** - Data pipeline
- `container.py`: DataContainer class - main entry point for data processing
- `preprocessing.py`: Rolling window smoothing, reindexing
- `features.py`: SIRD compartment calculations, rate calculations, logit transforms
- `validation.py`: Data validation and type checking

**`src/epydemics/models/`** - Modeling components
- `base.py`: BaseModel and SIRDModelMixin abstract classes
- `sird.py`: Model class - main model implementation
- `var_forecasting.py`: VARForecasting - VAR time series modeling
- `simulation.py`: EpidemicSimulation - Monte Carlo epidemic simulations
- `forecasting/var.py`: Additional VAR utilities

**`src/epydemics/analysis/`** - Post-processing and visualization (extracted in v0.6.0)
- `evaluation.py`: Model evaluation metrics (MAE, MSE, RMSE, MAPE, SMAPE)
  - `evaluate_forecast()`: Evaluate forecasts against actual data
  - `evaluate_model()`: Comprehensive model evaluation
- `visualization.py`: Plotting functions for results
  - `visualize_results()`: Main visualization function for compartments and rates
- `formatting.py`: Professional plot formatting utilities
  - `format_time_axis()`: Format datetime axes with appropriate intervals
  - `add_forecast_highlight()`: Add shaded regions for forecast periods
  - `set_professional_style()`: Apply consistent styling across plots
  - `format_subplot_grid()`: Configure subplot layouts

**`src/epydemics/utils/`** - Utilities
- `transformations.py`: Logit/inverse logit transforms, rate bound handling

### Key Classes and Their Roles

**DataContainer**: Entry point for all data processing
- Validates raw data format
- Applies rolling window smoothing (default 7 days)
- Orchestrates feature engineering pipeline
- Stores processed data with all SIRD variables

**Model** (in sird.py): Main modeling interface
- Inherits from BaseModel and SIRDModelMixin
- Wraps VARForecasting and EpidemicSimulation
- Provides high-level API: create_model(), fit_model(), forecast(), run_simulations()
- Delegates to specialized components for forecasting and simulation

**VARForecasting**: Time series modeling component
- Creates and fits VAR models on logit-transformed rates
- Generates confidence intervals for rate forecasts
- Handles inverse logit transformation back to rate space

**EpidemicSimulation**: Monte Carlo simulation engine
- Takes rate forecasts with confidence intervals
- Generates 27 scenarios (3 levels × 3 rates: upper/point/lower)
- Runs discrete SIRD simulations forward in time
- Computes central tendency measures (mean, median, gmean, hmean)

## Mathematical Foundation

### SIRD Compartments
```python
S = Susceptible = N - I - R - D  # Population not yet infected
I = Infected = C - R - D          # Currently infected
R = Recovered = C.shift(14) - D  # Recovered (14-day lag assumption)
D = Deaths = cumulative deaths   # Deceased
C = Cases = cumulative cases     # Total confirmed cases
A = S + I                         # Active susceptible + infected
```

### Time-Varying Rates
```python
α(t) = infection rate = (A * dC) / (I * S)
β(t) = recovery rate = dR / I
γ(t) = mortality rate = dD / I
```

### Critical Constraints
- Rates must be in (0, 1) for logit transformation
- S(t) and I(t) must be > 0 for α calculation
- Forward fill (ffill) used for missing rate values
- `prepare_for_logit_function()` ensures rate bounds before logit transform

### Feature Engineering Order
Must follow this exact sequence (implemented in `features.py`):
1. Calculate R using 14-day lag: `R = C.shift(14) - D`
2. Calculate I: `I = C - R - D`
3. Calculate differences (dC, dI, dR, dD)
4. Calculate rates (α, β, γ) from differences
5. Apply `prepare_for_logit_function()` to bound rates
6. Apply logit transform

## Common Development Patterns

### Typical Analysis Workflow
```python
from epydemics import DataContainer, Model, process_data_from_owid

# 1. Load and prepare data
raw_data = process_data_from_owid(iso_code="OWID_WRL")  # Global data
container = DataContainer(raw_data, window=7)

# 2. Create and fit model
model = Model(container, start="2020-03-01", stop="2020-12-31")
model.create_model()
model.fit_model(max_lag=10, ic="aic")

# 3. Forecast and simulate
model.forecast(steps=30)
model.run_simulations()
model.generate_result()

# 4. Evaluate and visualize
testing_data = container.data.loc[model.forecasting_interval]
model.visualize_results("C", testing_data, log_response=True)
evaluation = model.evaluate_forecast(testing_data)
```

### Parallel Simulations (Performance)

The library supports parallel execution of epidemic simulations for improved performance on multi-core systems.

#### Configuration

**Environment Variables / .env file:**
```bash
# Enable parallel execution (default: True)
PARALLEL_SIMULATIONS=True

# Number of parallel jobs (default: None = auto-detect CPU count)
N_SIMULATION_JOBS=4  # or None for auto-detection
```

**Python code:**
```python
from epydemics.core.config import get_settings

settings = get_settings()
print(f"Parallel simulations: {settings.PARALLEL_SIMULATIONS}")
print(f"Number of jobs: {settings.N_SIMULATION_JOBS}")
```

#### Usage Examples

**Auto-detect CPUs (default):**
```python
# Uses config default (parallel if PARALLEL_SIMULATIONS=True)
model.run_simulations()  # Auto-detects CPU count

# Explicitly use auto-detection
model.run_simulations(n_jobs=None)
```

**Specify number of workers:**
```python
# Use specific number of parallel workers
model.run_simulations(n_jobs=4)  # 4 parallel workers

# Force sequential execution (debugging or resource constraints)
model.run_simulations(n_jobs=1)
```

#### Performance Considerations

**When to use parallel:**
- Multiple CPU cores available
- Running single large analysis
- Forecast periods with many scenarios (27 scenarios = 3³ combinations)
- Production forecasting

**When to use sequential:**
- Debugging (easier to trace)
- Running many models simultaneously (avoid oversubscription)
- Limited memory
- Single-core systems

**Overhead vs Benefit:**
- **Process spawning overhead**: ~2-3 seconds (Windows)
- **Benefits when simulation time >> overhead** (production-scale data)
- **Not beneficial for quick simulations** (<1 second per run)

**Benchmark results (Windows, 16 cores, small test data):**
```
Sequential (n_jobs=1):  0.020s (baseline)
Parallel (n_jobs=2):    2.418s (120x SLOWER due to overhead)
Parallel (n_jobs=4):    2.751s (138x SLOWER)
Parallel (n_jobs=16):   7.196s (360x SLOWER)
```

**Key finding**: For small/quick simulations, sequential is faster. Parallel execution is beneficial when:
- Simulations take >5 seconds individually
- Working with large datasets (>1000 data points)
- Running production forecasts with many scenarios
- Simulation complexity justifies overhead

**Run your own benchmark:**
```bash
python benchmarks/parallel_simulation_benchmark.py
```

Results saved to `benchmarks/parallel_benchmark_report.md`

### Working with Constants
Always import and use predefined constants from `epydemics.core.constants`:
```python
from epydemics.core.constants import (
    RATIOS,                      # ["alpha", "beta", "gamma"]
    LOGIT_RATIOS,                # ["logit_alpha", "logit_beta", "logit_gamma"]
    COMPARTMENTS,                # ["A", "C", "S", "I", "R", "D"]
    COMPARTMENT_LABELS,          # {"A": "Active", "C": "Confirmed", ...}
    FORECASTING_LEVELS,          # ["lower", "point", "upper"]
    CENTRAL_TENDENCY_METHODS,    # ["mean", "median", "gmean", "hmean"]
    METHOD_NAMES,                # {"mean": "Mean", "median": "Median", ...}
    METHOD_COLORS,               # {"mean": "blue", "median": "orange", ...}
)
```

### Data Sources
- Primary: Our World in Data (OWID) COVID-19 dataset
- Required columns: `date`, `total_cases`, `total_deaths`, `population`
- ISO codes: `OWID_WRL` (global), country codes like `MEX`, `USA`
- Helper: `process_data_from_owid()` in `epydemics.py`

### Result Storage
Results use `python-box` for nested attribute access:
```python
# Forecasting results structure
model.forecasting_box.alpha.lower  # Lower CI for infection rate
model.forecasting_box.alpha.point  # Point forecast
model.forecasting_box.alpha.upper  # Upper CI

# Simulation results structure (27 scenarios)
model.results.simulation[alpha_level][beta_level][gamma_level].C  # Cases
```

## Testing Conventions

### Test Organization
- `tests/unit/` - Unit tests for individual components
  - `tests/unit/analysis/` - Analysis module tests
  - `tests/unit/core/` - Core functionality tests
  - `tests/unit/models/` - Model-specific unit tests
- `tests/integration/` - Integration tests for full workflows
  - `test_backward_compatibility.py` - Ensures API stability
- `tests/conftest.py` - Shared fixtures
- Top-level test files: `test_data_container.py`, `test_model.py`, `test_parallel_simulations.py`

### Test Markers
Use pytest markers to categorize tests:
```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.network  # Requires network access
```

### Running Specific Tests
```bash
# Run a specific test file
pytest tests/test_model.py

# Run a specific test function
pytest tests/test_model.py::test_function_name

# Run a specific test class
pytest tests/test_model.py::TestClassName

# Run a specific test method in a class
pytest tests/test_model.py::TestClassName::test_method_name

# Run with verbose output and show print statements
pytest tests/test_model.py -v -s

# Run with debugging on first failure
pytest tests/test_model.py -x --pdb
```

### Common Fixtures (in conftest.py)
- `sample_owid_data`: OWID-format epidemiological data (31 days, 2020-03-01 to 2020-03-31)
- `sample_processed_data`: Processed data with C, D, N columns and DatetimeIndex
- `sample_data_container`: Pre-initialized DataContainer with processed sample data
- All fixtures use `np.random.seed(42)` for reproducibility

## Code Style Requirements

### Critical: NO EMOJIS
Never use emojis in:
- Code comments or docstrings
- Commit messages
- Documentation
- Any output or communication

### Type Hints
- All functions must have type hints (enforced by mypy)
- Use `Optional[T]` for nullable types
- Use `Dict`, `List`, `Tuple` from typing for Python 3.9 compatibility
- Exception: Can use `tuple[str, ...]` in function signatures (Python 3.9+)

### Docstrings
- Use Google-style docstrings
- Required for all public classes and functions
- Include Args, Returns, Raises sections

### Formatting
- Line length: 88 characters (black default)
- Use black for code formatting
- Use isort with black profile for import sorting

## Common Pitfalls and Solutions

### Problem: "Cannot calculate alpha when S or I is zero"
**Cause**: Early in epidemic, S ≈ N or I = 0
**Solution**: Use `.loc[start:stop]` to select date range where I > 0

### Problem: "Rates outside (0, 1) bounds"
**Cause**: Data issues causing invalid rate calculations
**Solution**: Use `prepare_for_logit_function()` which clips to (ε, 1-ε)

### Problem: "NaN values in logit transform"
**Cause**: Zeros in rate data
**Solution**: Pipeline uses forward fill (ffill) to propagate last valid value

### Problem: "VAR model fails to fit"
**Cause**: Insufficient data or too many lags
**Solution**: Reduce `max_lag` parameter or increase training data range

## Important Files to Review

When making changes to specific functionality, review these key files:

**Data Processing**:
- `src/epydemics/data/features.py` - Feature engineering logic
- `src/epydemics/data/validation.py` - Data validation rules

**Modeling**:
- `src/epydemics/models/sird.py` - Main model API
- `src/epydemics/models/var_forecasting.py` - VAR forecasting logic
- `src/epydemics/models/simulation.py` - Simulation engine

**Configuration**:
- `pyproject.toml` - Project metadata, dependencies, tool configs
- `src/epydemics/core/config.py` - Runtime settings

**Examples**:
- `examples/global_forecasting.ipynb` - Complete COVID-19 analysis example
- `examples/parallel_simulation_demo.ipynb` - Parallel simulation demonstrations
- `examples/README.md` - Guide to example notebooks
- `examples/download_data.py` - Script to download OWID data
- `examples/DATA_SOURCES.md` - Information about data sources
- `examples/NETWORK_ISSUES.md` - Troubleshooting network/data download issues
