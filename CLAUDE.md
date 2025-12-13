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
- Current version: 0.9.0 (defined in `pyproject.toml`)
- Version also appears in `src/epydemics/__init__.py` as `__version__`
- Main branch: `main`
- When bumping versions, update both `pyproject.toml` (line 7) and `src/epydemics/__init__.py`
- **IMPORTANT**: These must be kept in sync. Check both files before releasing.

### Result Caching (v0.6.1+)
The library supports file-based caching of generated results to avoid recomputation when running the same analysis multiple times.

**Configuration via .env file:**
```bash
# Enable result caching (default: False)
RESULT_CACHING_ENABLED=True

# Cache directory (default: .epydemics_cache)
CACHE_DIR=.epydemics_cache

# Invalidate cache on version changes (default: False)
CACHE_STRICT_VERSION=False
```

**Cache Key Components:**
- Package version (if CACHE_STRICT_VERSION=True)
- Model parameters: start/stop dates, forecast steps
- Last historical data state (SHA-256 hash)
- Forecast values (SHA-256 hash)

**Usage:**
```python
# First run: computes and caches results
model.generate_result()  # Cache miss - full computation

# Subsequent runs with same configuration: loads from cache
model.generate_result()  # Cache hit - instant load
```

**Important:**
- Cache files are stored in `.epydemics_cache/` by default
- Add cache directory to `.gitignore` to avoid committing cache artifacts
- Cache invalidates automatically when data or model parameters change
- Set `CACHE_STRICT_VERSION=True` in production to invalidate cache on version changes

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
- `preprocessing.py`: Rolling window smoothing, frequency detection
- `features.py`: SIRD compartment calculations, rate calculations, logit transforms
- `validation.py`: Data validation and type checking (cumulative and incidence modes)
- `frequency_handlers.py`: Pluggable frequency handlers (Daily, Business Day, Weekly, Monthly, Annual)

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
- `seasonality.py`: Frequency-aware seasonal pattern detection (v0.9.0)
  - `SeasonalPatternDetector`: Adaptive threshold detection per frequency
  - Frequency-specific candidate periods (daily: 7/14/30/91/365, weekly: 4/13/26/52, etc.)

**`src/epydemics/utils/`** - Utilities
- `transformations.py`: Logit/inverse logit transforms, rate bound handling

### Caching Mechanism (v0.6.1+)

**Result Caching Flow**:
```
generate_result() → check cache → cache hit? → load from disk
                         ↓ (miss)
                    compute results → save to cache → return
```

The caching system in `Model.generate_result()` creates deterministic cache keys using:
- Model configuration (start, stop, forecast steps)
- Last historical data state (SHA-256 hash of values)
- Forecast values (SHA-256 hash)
- Package version (optional, if `CACHE_STRICT_VERSION=True`)

Cache files are stored as JSON in `CACHE_DIR` (default: `.epydemics_cache/`) with filenames based on the SHA-256 hash of the cache key.

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

### SIRDV Model Extension (v0.7.0+)
The SIRDV model extends SIRD by adding a Vaccinated compartment (V) and vaccination rate (δ).

**SIRDV Compartments:**
```python
V = Vaccinated = cumulative vaccinations  # Vaccinated population
S = Susceptible = N - I - R - D - V       # Updated to exclude V
I = Infected = C - R - D                  # Unchanged
R = Recovered = C.shift(14) - D           # Unchanged
D = Deaths = cumulative deaths            # Unchanged
C = Cases = cumulative cases              # Unchanged
A = S + I                                 # Active population
```

**SIRDV Rates:**
```python
δ(t) = vaccination rate = dV / S  # New vaccination rate
α(t) = infection rate = (A * dC) / (I * S)
β(t) = recovery rate = dR / I
γ(t) = mortality rate = dD / I
```

**Conservation Law:**
```python
# SIRD: N = S + I + R + D
# SIRDV: N = S + I + R + D + V
```

**Key Differences:**
- **4 rates instead of 3**: VAR model forecasts (logit_alpha, logit_beta, logit_gamma, logit_delta)
- **81 scenarios instead of 27**: Simulations run 3⁴ = 81 combinations (lower/point/upper for each rate)
- **4D Box structure**: `simulation[α][β][γ][δ]` for scenario storage
- **Vaccination flow**: `vaccination = δ * S` removes susceptible individuals to V compartment

**Configuration:**
```bash
# Enable SIRDV mode (requires vaccination column in data)
ENABLE_VACCINATION=True
VACCINATION_COLUMN=people_vaccinated  # Column name in OWID data
```

**Detection:**
```python
# Model automatically detects vaccination support
model = Model(container, start="2020-03-01", stop="2021-12-31")
print(model.has_vaccination)  # True if logit_delta present

# Results include V compartment when vaccination detected
model.generate_result()
print(model.results.V)  # Vaccination forecasts
```

**Performance Notes:**
- SIRDV requires more observations for VAR estimation (4 equations vs 3)
- Use longer training periods or smaller max_lag for SIRDV
- Simulation time ~3x longer due to 81 scenarios vs 27
- Parallel execution (`n_jobs=None`) recommended for SIRDV

### Native Multi-Frequency Support (v0.9.0)

Version 0.9.0 introduces **native multi-frequency support** without artificial reindexing. The system now processes epidemiological data in its native frequency (Daily, Business Day, Weekly, Monthly, Annual) using a pluggable handler architecture.

**Key v0.9.0 Features:**

- **Native Frequency Processing**: No artificial reindexing - data stays in native frequency
- **5 Supported Frequencies**: Daily (D), Business Day (B), Weekly (W), Monthly (ME), Annual (YE)
- **Pluggable Architecture**: `FrequencyHandler` base class with concrete implementations
- **Frequency-Aware VAR Defaults**: Automatic max_lag selection based on frequency
- **Frequency-Aware Aggregation**: Skips resampling when source and target frequencies match
- **Frequency-Aware Seasonality**: Adaptive seasonal pattern detection per frequency
- **Business Day Support**: Trading-day calendars (252 days/year) with validated lags
- **Backward Compatible**: All existing code works unchanged (defaults to daily)

**Frequency Handlers (v0.9.0):**
```python
from epydemics.data.frequency_handlers import (
    FrequencyHandlerRegistry,
    DailyFrequencyHandler,
    BusinessDayFrequencyHandler,
    WeeklyFrequencyHandler,
    MonthlyFrequencyHandler,
    AnnualFrequencyHandler,
)

# Automatic frequency detection and handler selection
registry = FrequencyHandlerRegistry()
handler = registry.get_handler("YE")  # Annual handler
print(handler.days_per_year)  # 365
print(handler.recovery_lag)   # 0 (rounded from 14/365 years)
print(handler.default_max_lag)  # 3 years

# Business day handler (new in v0.9.0)
bday_handler = registry.get_handler("B")
print(bday_handler.days_per_year)  # 252 (trading days)
print(bday_handler.recovery_lag)   # 10 (business days)
print(bday_handler.default_max_lag)  # 10 (conservative for VAR)
```

**Native Annual Data Workflow (v0.9.0):**
```python
from epydemics import DataContainer, Model
import pandas as pd
import numpy as np

# 1. Load annual measles data (native frequency - NO reindexing)
annual_data = pd.DataFrame({
    "C": np.cumsum(np.random.exponential(200, 40)),
    "D": np.cumsum(np.random.exponential(5, 40)),
    "N": [330000000] * 40,
}, index=pd.date_range("1980", periods=40, freq="YE"))

# DataContainer automatically detects frequency and uses appropriate handler
container = DataContainer(annual_data, window=1, frequency="YE")
print(container.frequency)  # "YE" (year-end)

# 2. Create model (no frequency conversion - stays annual)
model = Model(container, start="1982", stop="2010")
model.create_model()
model.fit_model(max_lag=3)  # Auto-selected based on annual frequency

# 3. Forecast in native annual frequency
model.forecast(steps=10)  # 10 YEARS, not days
model.run_simulations(n_jobs=1)
model.generate_result()

# Results are already in annual frequency - no aggregation needed
print(model.results.C)  # Annual case forecasts
```

**Incidence Mode for Eliminated Diseases (v0.9.0):**
```python
# Measles surveillance: incident cases (not cumulative)
measles_data = pd.DataFrame({
    "I": [220, 55, 667, 164, 81, 34, 12, 0, 0, 4, 18, 45, 103, 67, 89],  # Annual incident cases
    "D": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # Deaths
    "N": [110000000] * 15,  # Population
}, index=pd.date_range("2010", periods=15, freq="YE"))

# Use incidence mode (NEW in v0.9.0)
container = DataContainer(measles_data, window=1, frequency="YE", mode="incidence")
print(container.mode)  # "incidence"

# Model automatically inherits incidence mode
model = Model(container, start="2010", stop="2020")
print(model.mode)  # "incidence"

# Feature engineering handles incidence → cumulative conversion
# C = cumsum(I), then rates calculated identically
model.create_model()
model.fit_model(max_lag=3)
model.forecast(steps=5)  # 5 years
model.run_simulations(n_jobs=1)
model.generate_result()
```

**Frequency-Aware Aggregation (v0.9.0):**
```python
# Aggregation now detects source frequency and skips resampling when unnecessary
# Example: Daily forecasts → Annual aggregation
daily_model = Model(daily_container, start="2020-01", stop="2020-12")
daily_model.forecast(steps=365)

annual_forecast = daily_model.aggregate_forecast(
    "C",  # Compartment
    target_frequency="YE",  # Annual (use modern alias)
    aggregate_func="last",  # End-of-year value
    methods=["mean", "median"]  # Central tendency methods
)

# Example: Annual forecasts (already annual) → Annual aggregation (no resampling)
annual_model = Model(annual_container, start="2010", stop="2020")
annual_model.forecast(steps=10)

# No resampling occurs here (source=YE, target=YE)
annual_agg = annual_model.aggregate_forecast("C", target_frequency="YE", aggregate_func="last")
```

**Frequency-Aware Seasonality Detection (v0.9.0):**
```python
from epydemics.analysis.seasonality import SeasonalPatternDetector

# Automatic frequency-specific seasonality detection
detector = SeasonalPatternDetector()

# Daily data: checks for weekly, monthly, quarterly, annual patterns
daily_seasonality = detector.detect_seasonal_patterns(daily_data, frequency="D")
print(daily_seasonality)
# {'has_seasonality': True, 'periods': [7, 365], 'model_recommendation': 'ARIMA'}

# Annual data: no seasonal patterns (insufficient data)
annual_seasonality = detector.detect_seasonal_patterns(annual_data, frequency="YE")
print(annual_seasonality)
# {'has_seasonality': False, 'periods': [], 'model_recommendation': 'Simple VAR'}
```

**Supported Frequencies:**
```python
from epydemics.core.constants import (
    MODERN_FREQUENCY_ALIASES,
    RECOVERY_LAG_BY_FREQUENCY,
)

# Modern pandas frequency aliases (v0.9.0)
print(MODERN_FREQUENCY_ALIASES)
# {"D": "D", "W": "W", "M": "ME", "Y": "YE", "A": "YE", "B": "B"}

# Recovery lag by frequency (biological constant: 14 days)
print(RECOVERY_LAG_BY_FREQUENCY)
# {"D": 14, "W": 2, "M": 0.5, "Y": 0.038, "A": 0.038}
```

**Best Practices for Multi-Frequency Data (v0.9.0):**

1. **Always specify frequency explicitly** to avoid auto-detection errors
   ```python
   container = DataContainer(data, frequency="YE")  # Explicit
   ```

2. **Use modern pandas aliases** to avoid FutureWarnings
   - Use `"YE"` instead of `"Y"` or `"A"` for annual
   - Use `"ME"` instead of `"M"` for monthly
   - Use `"W"` for weekly (unchanged)
   - Use `"D"` for daily (unchanged)
   - Use `"B"` for business days (new)

3. **Match window size to frequency**
   - Annual: `window=1` (no smoothing)
   - Monthly: `window=1-3` (minimal smoothing)
   - Weekly: `window=1-4` (1-4 weeks)
   - Daily: `window=7-14` (1-2 weeks)
   - Business days: `window=5-10` (1-2 trading weeks)

4. **Use incidence mode for eliminated diseases** (measles, polio, rubella)
   ```python
   container = DataContainer(data, mode="incidence", frequency="YE")
   ```

5. **Trust frequency-aware defaults** for VAR parameters
   - System automatically selects appropriate `max_lag` based on frequency
   - Override only when domain knowledge suggests otherwise

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

### Result Caching (v0.6.1+)

Enable caching to avoid recomputing results for the same model configuration:

```python
from epydemics.core.config import get_settings
import os

# Enable caching via environment variable
os.environ["RESULT_CACHING_ENABLED"] = "True"

# Or configure via .env file:
# RESULT_CACHING_ENABLED=True
# CACHE_DIR=.epydemics_cache
# CACHE_STRICT_VERSION=False

model.generate_result()  # First run: computes and caches
model.generate_result()  # Subsequent runs: loads from cache
```

**Performance Benefits:**
- Instant result loading for repeated analyses
- Useful for iterative development and testing
- Cache automatically invalidates when data or parameters change

**Cache Management:**
```python
from pathlib import Path

# Clear cache manually if needed
cache_dir = Path(get_settings().CACHE_DIR)
if cache_dir.exists():
    import shutil
    shutil.rmtree(cache_dir)
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

### Incidence Mode for Eliminated Diseases (v0.9.0)

The library now supports **dual-mode data processing** for both cumulative and incidence (incident cases) data patterns.

**Key Insight**: The system forecasts **rates** (α, β, γ, δ), not compartments. After feature engineering converts incidence→cumulative, the forecasting and simulation engines work identically for both modes.

**Incidence Mode Use Cases:**
- Measles surveillance: Annual incident cases with sporadic outbreaks and elimination periods
- Eliminated diseases: Polio, rubella with variable annual incidence and non-monotonic patterns
- Outbreak data: Cases that increase → decrease → increase (unlike COVID-19 cumulative data)

**Mode Selection:**
```python
from epydemics import DataContainer

# Cumulative mode (default - COVID-19 style)
covid_data = pd.DataFrame({"C": cumulative_cases, "D": cumulative_deaths, "N": population})
container = DataContainer(covid_data, mode="cumulative")  # C as input, I derived

# Incidence mode (measles, polio, rubella style)
measles_data = pd.DataFrame({"I": incident_cases, "D": deaths, "N": population})
container = DataContainer(measles_data, mode="incidence", frequency="YE")  # I as input, C derived
```

**Feature Engineering Differences:**

| Mode | Input Compartments | Derived Compartments | Conservation Law |
|------|-------------------|---------------------|------------------|
| Cumulative | C (cumulative cases) | I = C - R - D | C = I + R + D |
| Incidence | I (incident cases) | C = cumsum(I) | Same after conversion |

**After feature engineering, both modes produce identical rate calculations:**
```python
# Both modes ultimately calculate:
α(t) = (A * dC) / (I * S)  # Infection rate
β(t) = dR / I               # Recovery rate
γ(t) = dD / I               # Mortality rate
# Rates are then logit-transformed and fed to VAR model
```

### Working with Constants
Always import and use predefined constants from `epydemics.core.constants`:
```python
from epydemics.core.constants import (
    RATIOS,                      # ["alpha", "beta", "gamma", "delta"] (v0.9.0: added delta)
    LOGIT_RATIOS,                # ["logit_alpha", "logit_beta", "logit_gamma", "logit_delta"]
    COMPARTMENTS,                # ["A", "C", "S", "I", "R", "D", "V"] (v0.7.0: added V)
    COMPARTMENT_LABELS,          # {"A": "Active", "C": "Confirmed", ...}
    FORECASTING_LEVELS,          # ["lower", "point", "upper"]
    CENTRAL_TENDENCY_METHODS,    # ["mean", "median", "gmean", "hmean"]
    METHOD_NAMES,                # {"mean": "Mean", "median": "Median", ...}
    METHOD_COLORS,               # {"mean": "blue", "median": "orange", ...}
    MODERN_FREQUENCY_ALIASES,    # {"D": "D", "W": "W", "M": "ME", "Y": "YE", "A": "YE", "B": "B"}
    RECOVERY_LAG_BY_FREQUENCY,   # {"D": 14, "W": 2, "M": 0.5, "Y": 0.038, "A": 0.038}
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

### VAR Model API Pattern
When working with statsmodels VAR models, use attribute access for information criteria:
```python
from statsmodels.tsa.api import VAR

# Create and select order
var_model = VAR(data)
selector = var_model.select_order(maxlags=max_lag)

# CORRECT: Access information criteria as attributes
optimal_lag_aic = selector.aic
optimal_lag_bic = selector.bic
optimal_lag_hqic = selector.hqic

# INCORRECT: Do NOT pass ic as parameter to select_order
# selector = var_model.select_order(maxlags=max_lag, ic="aic")  # Will fail

# Fit with selected lag
fitted = var_model.fit(optimal_lag_aic)
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
- `src/epydemics/data/features.py` - Feature engineering logic (cumulative and incidence modes)
- `src/epydemics/data/validation.py` - Data validation rules (dual-mode support)
- `src/epydemics/data/frequency_handlers.py` - Frequency handler implementations (v0.9.0)
- `src/epydemics/data/preprocessing.py` - Frequency detection and smoothing

**Modeling**:
- `src/epydemics/models/sird.py` - Main model API (mode-aware, frequency-aware)
- `src/epydemics/models/var_forecasting.py` - VAR forecasting logic (frequency-aware defaults)
- `src/epydemics/models/simulation.py` - Simulation engine (parallel/sequential)

**Analysis**:
- `src/epydemics/analysis/seasonality.py` - Frequency-aware seasonal pattern detection (v0.9.0)
- `src/epydemics/analysis/evaluation.py` - Model evaluation metrics
- `src/epydemics/analysis/visualization.py` - Plotting functions

**Configuration**:
- `pyproject.toml` - Project metadata, dependencies, tool configs
- `src/epydemics/core/config.py` - Runtime settings (caching, parallel simulations)
- `src/epydemics/core/constants.py` - Frequency aliases, recovery lags, compartments, rates
- `.env` - Environment configuration for caching and parallel execution (optional)

**Examples**:
- `examples/global_forecasting.ipynb` - Complete COVID-19 analysis example
- `examples/parallel_simulation_demo.ipynb` - Parallel simulation demonstrations
- `examples/README.md` - Guide to example notebooks
- `examples/download_data.py` - Script to download OWID data
- `examples/DATA_SOURCES.md` - Information about data sources
- `examples/NETWORK_ISSUES.md` - Troubleshooting network/data download issues

**Testing**:
- `tests/models/test_result_caching.py` - Result caching tests
- `tests/test_parallel_simulations.py` - Parallel simulation tests
- `tests/unit/data/test_incidence_mode.py` - Incidence mode unit tests (v0.9.0)
- `tests/integration/test_incidence_mode_workflow.py` - Incidence mode integration tests (v0.9.0)
- `tests/unit/analysis/test_seasonality.py` - Seasonal pattern detection tests (v0.9.0)

## What's New in v0.9.0 (Current Release)

This release represents a major architectural expansion enabling the library to handle diverse epidemiological data patterns beyond COVID-19.

**Native Multi-Frequency Support (Phases 4-7)**:
- **No More Reindexing**: Data stays in native frequency (Daily, Business Day, Weekly, Monthly, Annual)
- **Pluggable Architecture**: `FrequencyHandler` base class with 5 concrete implementations
- **Frequency-Aware Defaults**: Automatic `max_lag` selection per frequency (Annual: 3, Monthly: 6, Weekly: 8, Daily: 14, Business: 10)
- **Business Day Support**: Trading-day calendars (252 days/year) with validated recovery lags
- **Frequency-Aware Aggregation**: Skips resampling when source and target match
- **Seasonal Pattern Detection**: Adaptive thresholds and frequency-specific candidate periods

**Incidence Mode (Phase 2 - Measles Integration)**:
- **Dual-Mode Data Support**: Handle cumulative (COVID-19) and incidence (measles, polio, rubella) data
- **Mode-Aware Feature Engineering**: `I` as input for incidence mode, `C` derived via cumsum
- **Eliminated Disease Support**: Non-monotonic patterns, elimination periods (0 cases), sporadic reintroduction
- **Transparent Integration**: Mode propagates automatically from DataContainer → Model → Results
- **Zero Breaking Changes**: Existing cumulative mode code works unchanged

**Key Architectural Changes**:
1. **DataContainer API**: New `frequency` and `mode` parameters (both optional, backward compatible)
2. **Validation Split**: Separate validators for cumulative vs incidence data patterns
3. **Constants Expansion**: `MODERN_FREQUENCY_ALIASES`, `RECOVERY_LAG_BY_FREQUENCY` mappings
4. **New Modules**:
   - `src/epydemics/data/frequency_handlers.py` - Handler implementations
   - `src/epydemics/analysis/seasonality.py` - Pattern detection

**Performance & Testing**:
- 394 tests passing (32 skipped for optional dependencies)
- +27 new tests for incidence mode (21 unit + 6 integration)
- +13 new tests for seasonal pattern detection
- +12 new tests for business day support
- Zero regressions - 100% backward compatible

**When to Use v0.9.0 Features**:

| Use Case | Frequency | Mode | Example |
|----------|-----------|------|---------|
| COVID-19 daily data | `"D"` | `"cumulative"` | Daily confirmed cases (monotonic) |
| Stock/trading analysis | `"B"` | `"cumulative"` | Business day data (252 days/year) |
| Weekly disease reports | `"W"` | `"cumulative"` or `"incidence"` | Weekly case counts |
| Monthly surveillance | `"ME"` | `"incidence"` | Monthly incident cases |
| Annual measles data | `"YE"` | `"incidence"` | Annual sporadic outbreaks |

**Migration from v0.8.0 or earlier**:
```python
# Old way (v0.8.0): Annual data reindexed to daily with warnings
container = DataContainer(annual_data, window=1)  # Created ~13,500 artificial rows

# New way (v0.9.0): Native annual processing
container = DataContainer(annual_data, window=1, frequency="YE", mode="incidence")  # 40 rows stay 40 rows
```
