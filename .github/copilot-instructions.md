# GitHub Copilot Instructions for Epydemics

**Version 0.6.1-dev** - SIRDV Model Implementation Complete

## Project Overview
Epydemics implements epidemiological forecasting by combining discrete SIRD/SIRDV models with VAR (Vector Autoregression) time series on **logit-transformed rates**. The system now automatically detects and handles both traditional SIRD models and modern SIRDV models with vaccination data.

**Key Innovation**: Rates are logit-transformed before VAR modeling to ensure (0,1) bounds, then inverse-transformed for Monte Carlo epidemic simulations across 27 scenarios (3³ confidence levels). The system dynamically adapts to available data (SIRD vs SIRDV).

**Current Status**: Branch `sirdv-model-implementation` - **COMPLETE** ✅
- Dynamic SIRD/SIRDV detection implemented
- Vaccination support fully functional
- Result caching working with variable compartments
- All fast tests passing (130+)
- Slow tests properly marked

**Important**: Version in `pyproject.toml` is `0.6.1-dev` and `src/epydemics/__init__.py` should match before release.

## Architecture at a Glance

### Data Flow Pipeline
```
OWID CSV → DataContainer → Feature Engineering → Model → VAR Forecast → Simulation → Results
  ↓           ↓                 ↓                  ↓          ↓             ↓
Validate   Smooth(7d)      SIRD+Rates        Logit→VAR   27 Scenarios  Evaluation
          Rename→C,D,N    α,β,γ+Logit      Confidence   MonteCarlo    Viz+Metrics
```

### Critical Module Structure
- **`src/epydemics/core/`**: Constants (`RATIOS`, `COMPARTMENTS`), config (pydantic-settings), exceptions
- **`src/epydemics/data/container.py`**: `DataContainer` - orchestrates preprocessing pipeline
- **`src/epydemics/models/sird.py`**: `Model` - main API delegating to forecasting/simulation engines
- **`src/epydemics/models/simulation.py`**: `EpidemicSimulation` - **parallel/sequential** simulation with `n_jobs`
- **`src/epydemics/models/forecasting/var.py`**: `VARForecaster` - statsmodels VAR wrapper
- **`src/epydemics/analysis/`**: Evaluation metrics + visualization with professional formatting

## Mathematical Foundation

### SIRD Compartments (Order-Dependent Calculation)
```python
# MUST follow this sequence in feature_engineering():
R = C.shift(14) - D  # 1. Recovered (14-day lag assumption)
I = C - R - D        # 2. Infected (active cases)
S = N - I - R - D    # 3. Susceptible (remaining population)
A = S + I            # 4. Active (for rate calculations)
```

### Time-Varying Rates
```python
α(t) = (A * dC) / (I * S)  # Infection rate (requires I>0, S>0)
β(t) = dR / I              # Recovery rate
γ(t) = dD / I              # Mortality rate
# All rates → prepare_for_logit_function() → clip to (ε, 1-ε) → logit transform
```

**Critical Constraint**: Rates MUST be (0,1) for logit transform. Use `prepare_for_logit_function()` to clip rates, then `ffill()` for NaN propagation.

## Essential Development Patterns

### Standard Analysis Workflow
```python
from epydemics import DataContainer, Model, process_data_from_owid

# 1. Load data (auto-validates OWID format)
raw = process_data_from_owid(iso_code="OWID_WRL")  # or "MEX", "USA"
container = DataContainer(raw, window=7)

# 2. Create model with date range
model = Model(container, start="2020-03-01", stop="2020-12-31")
model.create_model()
model.fit_model(max_lag=10, ic="aic")  # VAR lag selection

# 3. Forecast and simulate (NEW: parallel support)
model.forecast(steps=30)
model.run_simulations(n_jobs=None)  # None=auto-detect CPUs, 1=sequential
model.generate_result()

# 4. Evaluate
testing_data = container.data.loc[model.forecasting_interval]
evaluation = model.evaluate_forecast(testing_data)
model.visualize_results("C", testing_data, log_response=True)
```

### Always Use Constants from `epydemics.core.constants`
```python
from epydemics.core.constants import (
    RATIOS,              # ["alpha", "beta", "gamma"]
    LOGIT_RATIOS,        # ["logit_alpha", "logit_beta", "logit_gamma"]
    COMPARTMENTS,        # ["A", "C", "S", "I", "R", "D"]
    FORECASTING_LEVELS,  # ["lower", "point", "upper"]
    CENTRAL_TENDENCY_METHODS  # ["mean", "median", "gmean", "hmean"]
)
```

### Configuration via Pydantic Settings
```python
from epydemics.core.config import get_settings

settings = get_settings()  # Cached singleton
# Configure via environment variables or .env:
# WINDOW_SIZE=7, RECOVERY_LAG=14, PARALLEL_SIMULATIONS=True
# N_SIMULATION_JOBS=4 (or None for CPU auto-detect)

# Result caching (v0.6.1+):
# RESULT_CACHING_ENABLED=True
# CACHE_DIR=.epydemics_cache
# CACHE_STRICT_VERSION=False  # True invalidates cache on version change

# Vaccination support (v0.6.1+):
# ENABLE_VACCINATION=True
# VACCINATION_COLUMN=people_vaccinated
```

## Critical Development Workflows

### Testing Commands
```bash
# Run all tests (uses pytest.ini markers)
pytest

# Specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests

# With coverage (configured in pyproject.toml)
pytest --cov=src/epydemics --cov-report=html

# Parallel execution
pytest -n auto
```

### Code Quality Pipeline (Pre-commit)
```bash
# Format + lint (order matters)
black src/ tests/           # Line length: 88
isort src/ tests/           # Import sorting (black profile)
flake8 src/ tests/          # Linting (E203, W503 ignored)
mypy src/                   # Type checking (strict mode)

# Run all pre-commit hooks
pre-commit run --all-files

# Install hooks (runs on git commit)
pre-commit install
```

### VAR Model API Pattern (Recent Fix)
```python
# INCORRECT (old usage - will fail):
selector = model.select_order(maxlags=max_lag, ic="aic")  # ic NOT accepted

# CORRECT (current implementation in var.py):
selector = model.select_order(maxlags=max_lag)
optimal_lag = getattr(selector, "aic", selector.aic)  # Access .aic, .bic, .hqic attributes
fitted = model.fit(optimal_lag)
```

## Project-Specific Conventions

### Parallel Simulation Pattern (v0.6.0+)
```python
# Module-level function for pickling (multiprocessing requirement)
def _run_single_simulation(data, forecasting_box, interval, levels):
    temp_sim = EpidemicSimulation(data, forecasting_box, interval)
    return (levels, temp_sim.simulate_for_given_levels(levels))

# In EpidemicSimulation.run_simulations():
with ProcessPoolExecutor(max_workers=n_jobs) as executor:
    futures = {executor.submit(_run_single_simulation, ...): scenario}
    # Collect results via as_completed()
```

### Result Storage with python-box
```python
# Nested attribute access (not dict keys)
model.forecasting_box.alpha.lower   # Lower CI
model.forecasting_box.alpha.point   # Point forecast  
model.forecasting_box.alpha.upper   # Upper CI

# 27 simulation scenarios (3×3×3 confidence levels)
model.simulation["lower"]["point"]["upper"]  # DataFrame with SIRD compartments
```

### Type Hints (Enforced by mypy)
```python
from typing import Optional, Dict, List, Tuple

def forecast(self, steps: int, alpha: float = 0.05) -> None:
    """Type hints required for all public methods."""
    pass

# Exception: Python 3.9+ tuples in signatures OK
def process(data: pd.DataFrame) -> tuple[str, ...]:
    pass
```

## Common Pitfalls & Solutions

### 1. "Cannot calculate alpha when S or I is zero"
**Cause**: Early epidemic data where S ≈ N or I = 0  
**Solution**: Use `.loc[start:stop]` to select date range after epidemic starts (I > 0)

### 2. "NaN values in logit transform"
**Cause**: Zeros or out-of-bounds rates  
**Solution**: Pipeline auto-applies `prepare_for_logit_function()` + `ffill()` - ensure feature engineering order is correct

### 3. VAR model fails with "singular matrix"
**Cause**: Insufficient data for lag order  
**Solution**: Reduce `max_lag` parameter or increase training period length

### 4. Slow simulation performance
**Solution**: Use `model.run_simulations(n_jobs=None)` for auto-detected parallel execution (4-7x speedup on multi-core)

## Style Requirements (Critical)

### NO EMOJIS Rule
Never use emojis in:
- Code comments/docstrings
- Commit messages
- Documentation
- Any output

Use clear, professional text only.

### Docstrings (Google Style)
```python
def forecast(self, steps: int) -> None:
    """
    Generate VAR forecasts for epidemic rates.

    Args:
        steps: Number of time steps to forecast

    Raises:
        RuntimeError: If model not fitted
        ValueError: If steps < 1

    Example:
        >>> model.forecast(steps=30)
    """
```

## Key Files for Common Tasks

**Modify Data Processing**: `src/epydemics/data/features.py` (feature engineering logic)  
**Modify Modeling API**: `src/epydemics/models/sird.py` (main Model class)  
**Modify Simulation Logic**: `src/epydemics/models/simulation.py` (parallel/sequential execution)  
**Add Configuration**: `src/epydemics/core/config.py` (pydantic Settings)  
**View Examples**: `examples/global_forecasting.ipynb` (complete COVID-19 analysis)  
**Test Patterns**: `tests/conftest.py` (fixtures: `sample_data`, `sample_container`)

## Integration Points

- **External Data**: OWID GitHub repo (auto-fetched by `process_data_from_owid()`)
- **Time Series**: statsmodels VAR (wrapped in `VARForecaster`)
- **Parallel Processing**: `concurrent.futures.ProcessPoolExecutor` (Python stdlib)
- **Config Management**: Environment variables via pydantic-settings (`.env` file support)

## Recent Major Changes (v0.6.1-dev)

1. **✅ SIRDV Model Support (COMPLETE - Nov 2025)**: 
   - Automatic detection of vaccination column (V)
   - Dynamic rate calculation including delta (vaccination rate)
   - Modified susceptible calculation: `S = N - C - V` for SIRDV
   - Backward compatible with SIRD models
   - See `SIRDV_IMPLEMENTATION_COMPLETE.md` for details

2. **✅ Result Caching (v0.6.1)**: File-based caching of `generate_result()` output to avoid recomputation
   - Configure via `.env`: `RESULT_CACHING_ENABLED=True`, `CACHE_DIR=.epydemics_cache`, `CACHE_STRICT_VERSION=False`
   - Cache key based on: model params, data state (SHA-256), forecast values, optionally package version
   - Dynamic compartment saving/loading (handles both SIRD and SIRDV)
   
3. **✅ Parallel Simulations (v0.6.0)**: Added `n_jobs` parameter to `run_simulations()` with auto-CPU detection

4. **✅ VAR API Fix (v0.6.0)**: Corrected `select_order()` usage (no `ic` parameter - use attribute access)

5. **✅ Modular Architecture (v0.6.0)**: Extracted analysis functions to `epydemics/analysis/` module

6. **✅ Modern Pandas (v0.6.0)**: Replaced deprecated `fillna(method="ffill")` with `.ffill()`

7. **✅ Test Infrastructure**: Added `@pytest.mark.slow` to 25+ integration tests for faster CI/CD

## Testing New Features
- **Result Caching**: `tests/models/test_result_caching.py` - cache hit/miss, invalidation, version handling
- **Parallel Simulations**: `tests/test_parallel_simulations.py` - sequential vs parallel equivalence, n_jobs validation
- **Vaccination**: `tests/unit/data/test_features_vaccination.py` - SIRDV feature engineering patterns
