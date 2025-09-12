# GitHub Copilot Instructions for Epydemics

**Version 0.5.0** - AI-Enhanced Documentation Release

## Project Overview
Epydemics implements a novel epidemiological forecasting system that combines discrete SIRD (Susceptible-Infected-Recovered-Deaths) mathematical models with time series analysis. Unlike classical epidemiological models with constant parameters, this project models time-varying infection, recovery, and mortality rates (α, β, γ) using VAR (Vector Autoregression) time series on logit-transformed rates.

## Core Architecture

### Main Components
- **`epydemics.py`**: Single-file module containing all core functionality
- **`DataContainer`**: Handles data preprocessing, feature engineering, and SIRD compartment calculations
- **`Model`**: Implements VAR time series modeling on logit-transformed rates and epidemic simulations

### Mathematical Foundation
The project uses a discrete SIRD model where rates vary over time:
```
α(t) = (S(t)+I(t))/(S(t)I(t)) * ΔC(t)  # Infection rate
β(t) = ΔR(t)/I(t)                      # Recovery rate
γ(t) = ΔD(t)/I(t)                      # Mortality rate
```

Key insight: Rates are logit-transformed before VAR modeling to ensure they stay within (0,1) bounds.

## Development Patterns

### Data Pipeline Flow
1. **Raw Data**: OWID CSV format with columns `['date', 'total_cases', 'total_deaths', 'population']`
2. **DataContainer**: Renames to `['C', 'D', 'N']`, applies rolling window smoothing, feature engineering
3. **Feature Engineering**: Calculates SIRD compartments (S, I, R, D), differences (dC, dI, etc), rates (α, β, γ)
4. **Logit Transform**: `logit_alpha = log(alpha/(1-alpha))` for VAR modeling
5. **Model**: VAR on logit rates → forecast → inverse transform → epidemic simulation

### Essential Constants
Always use these predefined lists from the module:
```python
ratios = ["alpha", "beta", "gamma"]
logit_ratios = ["logit_alpha", "logit_beta", "logit_gamma"]
compartments = ["A", "C", "S", "I", "R", "D"]
forecasting_levels = ["lower", "point", "upper"]
central_tendency_methods = ["mean", "median", "gmean", "hmean"]
```

### Key Method Patterns
- **Data validation**: Always use `validate_data()` before processing
- **Rate bounds**: Rates must be in (0,1) - use `prepare_for_logit_function()`
- **Forward fill**: Missing values filled with `fillna(method="ffill")`
- **Box objects**: Results stored in `python-box` objects for nested attribute access

## Development Workflows

### Typical Analysis Pattern
```python
# 1. Load and prepare data
data = process_data_from_owid(iso_code="OWID_WRL")  # Global data
container = DataContainer(data)

# 2. Create and fit model
model = Model(container, start="2020-03-01", stop="2020-12-31")
model.create_logit_ratios_model()
model.fit_logit_ratios_model()

# 3. Forecast and simulate
model.forecast_logit_ratios(steps=30)
model.run_simulations()
model.generate_result()

# 4. Evaluate and visualize
testing_data = container.data.loc[model.forecasting_interval]
model.visualize_results("C", testing_data, log_response=True)
evaluation = model.evaluate_forecast(testing_data)
```

### Submodule Management
This project uses git submodules for tutorials and examples:
- Use `./manage_tutorial.sh init` to initialize submodules
- Use `./manage_tutorial.sh update` to get latest content
- **Never modify** submodule content directly in this repo

### Testing and Validation
- Model validation uses multiple metrics: MAE, MSE, RMSE, MAPE, SMAPE
- Forecasts generate uncertainty bands through Monte Carlo simulation across rate confidence intervals
- Always test on held-out data using `model.evaluate_forecast()`

## Data Integration

### OWID Data Format
External data must match OWID structure:
- Required columns: `date`, `total_cases`, `total_deaths`, `population`
- ISO codes for filtering: `OWID_WRL` (global), country codes like `MEX`
- Data automatically reindexed to daily frequency with forward fill

### Rate Calculation Dependencies
Critical constraint: Infection rate calculation requires both S(t) and I(t) > 0:
```python
alpha = (data.A * data.dC) / (data.I * data.S)  # Will fail if I=0 or S=0
```

### Feature Engineering Order
Must follow this sequence in `feature_engineering()`:
1. Calculate R (recovered) using 14-day lag: `R = C.shift(14) - D`
2. Calculate I (infected): `I = C - R - D`
3. Calculate differences (dC, dI, etc.)
4. Calculate rates (α, β, γ) from differences
5. Apply logit transform

## Project-Specific Conventions

### Error Handling
- Custom exception: `NotDataFrameError` for type validation
- Extensive try-catch blocks with descriptive error messages
- Rate bounds checking with NaN replacement and forward fill

### Logging
Uses Python logging at INFO level. Matplotlib warnings suppressed to reduce noise during analysis.

### Simulation Architecture
Forecasting generates 3×3×3=27 scenarios by combining confidence intervals (lower/point/upper) for each rate. Results stored in nested Box structure: `simulation[alpha_level][beta_level][gamma_level]`

### Visualization Standards
- Gray dotted lines for individual simulation paths
- Colored lines for central tendencies (mean=blue, median=orange, gmean=green, hmean=purple)
- Red solid line for actual data comparison
- Logarithmic scale recommended for case/death counts

## Critical Dependencies
- `statsmodels.tsa.api.VAR` for time series modeling
- `python-box` for nested result containers
- `scipy.stats.gmean/hmean` for robust central tendency
- `pandas` with DatetimeIndex for time series operations

## AI Coding Guidelines

### Style Requirements
- **NO EMOJIS**: Never use emojis in code, documentation, commit messages, or any output
- Clean, professional text only in all communications
- Focus on clear, descriptive language without decorative symbols
