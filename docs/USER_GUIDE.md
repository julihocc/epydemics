# Epydemics User Guide

**Version**: 0.9.0-dev  
**Last Updated**: December 2025

## Table of Contents

1. [When to Use Epydemics](#when-to-use-epydemics)
2. [When NOT to Use](#when-not-to-use)
3. [Data Preparation Guide](#data-preparation-guide)
4. [Working with Different Data Frequencies](#working-with-different-data-frequencies)
5. [Incidence Mode (v0.9.0+)](#incidence-mode-v090)
6. [Annual Surveillance Data Workaround](#annual-surveillance-data-workaround)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Additional Resources](#additional-resources)

---

## When to Use Epydemics

Epydemics is designed for **epidemiological forecasting** using discrete compartmental models (SIRD/SIRDV) combined with VAR time series analysis. It works best for:

### Ideal Use Cases

**1. COVID-19 and Similar Emerging Epidemics**
- **Data Type**: Daily cumulative confirmed cases and deaths
- **Pattern**: Ongoing epidemic with continuous growth
- **Frequency**: Daily or weekly observations
- **Example**: OWID COVID-19 data
```python
from epydemics import process_data_from_owid, DataContainer, Model

# Load daily COVID-19 data
data = process_data_from_owid(iso_code="USA")
container = DataContainer(data, window=7)

# Model and forecast
model = Model(container, start="2020-03-01", stop="2020-12-31")
model.create_model()
model.fit_model(max_lag=10)
model.forecast(steps=30)
model.run_simulations(n_jobs=None)
model.generate_result()
```

**2. Influenza and Seasonal Epidemics**
- **Data Type**: Weekly incident cases or cumulative
- **Pattern**: Seasonal outbreaks with clear cyclical patterns
- **Frequency**: Weekly observations
- **Note**: Weekly data works well natively in v0.8.0

**3. Vaccine-Preventable Diseases (with vaccination data)**
- **Data Type**: Cases, deaths, AND vaccination coverage
- **Model**: SIRDV (with V compartment)
- **Example**: Measles with vaccination campaigns
```python
# SIRDV with vaccination data
data = pd.DataFrame({
    'C': cumulative_cases,
    'D': cumulative_deaths,
    'V': people_vaccinated,  # Vaccination coverage
    'N': population
}, index=date_index)

container = DataContainer(data, window=7)
# SIRDV model automatically detected
```

---

## When NOT to Use

Epydemics may not be suitable for:

### ❌ Very Sparse Data
- **Limitation**: < 20 time points
- **Reason**: Insufficient data for VAR model estimation
- **Alternative**: Consider simpler statistical models or SIR-only approaches

### ❌ Native Annual Data (v0.8.0)
- **Limitation**: Annual surveillance data (e.g., measles 1980-2020)
- **Reason**: System reindexes annual to daily via forward-fill, creating artificial patterns
- **Workaround**: Use Phase 1 temporal aggregation (see below)
- **Future**: Native annual support planned for v0.9.0

### ❌ Non-Infectious Diseases
- **Limitation**: Diseases without transmission dynamics
- **Reason**: SIRD compartmental model assumes susceptible→infected→recovered/dead flow
- **Examples**: Cancer, heart disease, genetic conditions

### ❌ Vector-Borne Diseases (without modification)
- **Limitation**: Diseases requiring vector compartments (mosquitoes, ticks)
- **Examples**: Malaria, dengue, Lyme disease
- **Note**: Would need custom compartmental model extensions

---

## Data Preparation Guide

### Required Data Format

Epydemics expects a pandas DataFrame with:

```python
import pandas as pd

data = pd.DataFrame({
    'C': [100, 250, 450, ...],      # Cumulative confirmed cases (required)
    'D': [5, 12, 23, ...],           # Cumulative deaths (required)
    'N': [1000000, 1000000, ...],    # Population (required)
    'V': [0, 5000, 12000, ...]       # Vaccinated count (optional, for SIRDV)
}, index=pd.date_range('2020-01-01', periods=100, freq='D'))
```

### Cumulative vs Incidence Data

**Cumulative Data (Current Default)**
- Values MUST be monotonically increasing
- Represents total cases up to that date
- Example: Total COVID-19 cases = 100 → 250 → 450

```python
# If you have cumulative data (COVID-19 style)
container = DataContainer(cumulative_data, window=7)
```

**Incidence Data (v0.9.0+)**
- Values can fluctuate up and down
- Represents NEW cases in that period
- Example: Annual measles = 200 → 50 → 180

```python
# FUTURE API (v0.9.0) - NOT AVAILABLE in v0.8.0
container = DataContainer(incidence_data, mode='incidence', frequency='Y')
```

**Converting Incidence to Cumulative (v0.8.0 Workaround)**
```python
# If you have incidence data, convert to cumulative
data['C'] = data['incident_cases'].cumsum()
data['D'] = data['incident_deaths'].cumsum()

# Then use as normal
container = DataContainer(data, window=1)  # window=1 for pre-cumulated data
```

### Frequency Requirements

| Frequency | Code | Status | Notes |
|-----------|------|--------|-------|
| Daily | `D` | ✅ Native | Preferred, most tested |
| Weekly | `W` | ✅ Native | Works well, set `window=1` |
| Monthly | `M` | ⚠️ Workaround | Use aggregation after forecast |
| Annual | `Y` | ⚠️ Workaround | Phase 1 solution (see below) |

---

## Working with Different Data Frequencies

### Daily Data (Recommended)

```python
# COVID-19 daily data
data = process_data_from_owid(iso_code="USA")
container = DataContainer(data, window=7)  # 7-day smoothing
```

### Weekly Data

```python
# Weekly influenza surveillance
weekly_data = pd.DataFrame({
    'C': cumulative_cases,
    'D': cumulative_deaths,
    'N': population
}, index=pd.date_range('2020-01-01', periods=52, freq='W'))

container = DataContainer(weekly_data, window=1)  # No smoothing needed
```

### Monthly Data → Daily Forecast → Monthly Output

```python
# Load monthly data (will be reindexed to daily internally)
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message=".*FREQUENCY MISMATCH.*")
    container = DataContainer(monthly_data, window=1)

# Forecast in daily resolution
model = Model(container, start="2020-01", stop="2021-12")
model.create_model()
model.fit_model(max_lag=3)
model.forecast(steps=365)  # 1 year
model.run_simulations(n_jobs=None)
model.generate_result()

# Aggregate back to monthly
monthly_forecast = model.aggregate_forecast(
    "C", 
    target_frequency="M",
    aggregate_func="last",  # End-of-month value
    methods=["mean", "median"]
)
```

---

## Annual Surveillance Data Workaround

**⚠️ Important**: This is a Phase 1 workaround. Native annual support coming in v0.9.0.

### The Challenge

Annual surveillance data (e.g., measles 1980-2020) presents unique challenges:
- Only 40 data points for 40 years
- Data is reindexed to daily (365 × 40 = 14,600 points)
- Forward-fill creates artificial patterns

### Recommended Workflow (v0.8.0)

```python
import pandas as pd
import numpy as np
import warnings
from epydemics import DataContainer, Model

# 1. Load annual measles data
annual_data = pd.DataFrame({
    "C": np.cumsum([200, 180, 150, ...]),  # Cumulative cases
    "D": np.cumsum([5, 4, 3, ...]),        # Cumulative deaths
    "N": [330000000] * 40,                  # Population
}, index=pd.date_range("1980", periods=40, freq="YE"))  # Year-end

# 2. Suppress frequency warning (we understand the limitation)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message=".*FREQUENCY MISMATCH.*")
    container = DataContainer(annual_data, window=1)

# 3. Create model and forecast (internally daily)
model = Model(container, start="1982", stop="2010")
model.create_model()
model.fit_model(max_lag=3)
model.forecast(steps=365 * 10)  # 10 years in days
model.run_simulations(n_jobs=1)
model.generate_result()

# 4. Aggregate daily forecasts back to annual
annual_forecast = model.aggregate_forecast(
    "C",                      # Compartment
    target_frequency="Y",     # Annual
    aggregate_func="last",    # End-of-year value
    methods=["mean", "median"]
)

print(annual_forecast.head())
#             mean     median  lower|lower|lower  ...
# 2010-12-31  1234.5   1200.3  1100.2            ...
# 2011-12-31  1456.7   1420.1  1300.4            ...
```

### Aggregation Strategies

```python
# Different ways to aggregate annual data

# Total new cases per year (sum daily increments)
annual_totals = model.aggregate_forecast("C", target_frequency="Y", aggregate_func="sum")

# Average daily cases throughout year
annual_average = model.aggregate_forecast("C", target_frequency="Y", aggregate_func="mean")

# End-of-year cumulative total
annual_cumulative = model.aggregate_forecast("C", target_frequency="Y", aggregate_func="last")

# Peak cases during year
annual_peak = model.aggregate_forecast("C", target_frequency="Y", aggregate_func="max")
```

### Understanding the Warning

When you load annual data, you'll see:

```
⚠️ FREQUENCY MISMATCH WARNING
Source data frequency: annual (Y)
Target frequency: daily (D)

Reindexing annual data to daily creates 13,516 rows via forward-fill,
which may produce meaningless rate calculations and forecasts.

Recommended actions:
1. Use native frequency support (v0.9.0+): frequency='Y'
2. Use temporal aggregation to convert forecasts back to annual
3. See documentation for annual surveillance data best practices
```

**This is expected** for Phase 1. Use temporal aggregation to work around it.

---

## Best Practices

### 1. Data Quality

✅ **DO:**
- Use at least 50+ time points for training
- Verify cumulative data is monotonically increasing
- Check for missing dates and handle gaps
- Use appropriate smoothing (window=7 for noisy daily data)

❌ **DON'T:**
- Mix cumulative and incidence data formats
- Use data with large gaps without interpolation
- Ignore validation warnings

### 2. Model Configuration

✅ **DO:**
- Start with `max_lag=10` for initial exploration
- Use AIC for lag selection: `model.fit_model(max_lag=10, ic="aic")`
- Forecast reasonable horizons (30-90 days for daily data)
- Use parallel simulations: `n_jobs=None` (auto-detect CPUs)

❌ **DON'T:**
- Over-forecast (> 6 months ahead gets unreliable)
- Use too many lags (max_lag > data points / 3)
- Run simulations sequentially on multi-core systems

### 3. Annual Data (v0.8.0)

✅ **DO:**
- Use `window=1` (no smoothing)
- Suppress frequency warnings if you understand limitations
- Always aggregate forecasts back to annual
- Test with smaller date ranges first

❌ **DON'T:**
- Trust daily-resolution results directly
- Use for high-stakes decisions without validation
- Ignore the limitations documented here

---

## Troubleshooting

### "Cannot calculate alpha when S or I is zero"

**Cause**: Early epidemic data where susceptible ≈ population or infected = 0

**Solution**: Start after epidemic begins
```python
# Skip early dates with no infections
model = Model(container, start="2020-03-10", stop="2020-12-31")  # Not Jan 1
```

### "NaN values in logit transform"

**Cause**: Rates outside (0, 1) bounds or zero denominators

**Solution**: Automatic in v0.8.0 - pipeline applies `prepare_for_logit_function()` + `ffill()`

Check feature engineering order is correct (S, I, R calculated in sequence)

### "Singular matrix" in VAR fitting

**Cause**: Insufficient data for chosen lag order

**Solution**: Reduce lag or increase training period
```python
model.fit_model(max_lag=5)  # Instead of 10
# OR use longer training period
model = Model(container, start="2020-01-01", stop="2021-12-31")
```

### Slow Simulation Performance

**Solution**: Enable parallel execution
```python
# Auto-detect CPUs (4-7x speedup on multi-core)
model.run_simulations(n_jobs=None)

# Or specify cores
model.run_simulations(n_jobs=4)

# Sequential (slow, for debugging)
model.run_simulations(n_jobs=1)
```

---

## Incidence Mode (v0.9.0+)

**New in v0.9.0**: Native support for **incidence data** (incident cases per period) without requiring conversion to cumulative format.

### Understanding Incidence vs Cumulative

**Cumulative Mode** (default):
- Input: Total cumulative cases `C` (monotonically increasing)
- Derived: Incident cases `I = dC/dt` (calculated from differences)
- Use case: COVID-19, flu pandemics, most OWID data

**Incidence Mode** (v0.9.0+):
- Input: Incident cases per period `I` (can vary up/down)
- Derived: Cumulative cases `C = cumsum(I)` (generated automatically)
- Use case: Measles, polio, vaccine-preventable diseases with elimination cycles

### When to Use Incidence Mode

✅ **Use `mode='incidence'` when:**
- Data reports **new cases per time period** (not running totals)
- Cases can **decrease between periods** (e.g., outbreak → elimination)
- Disease: Near-elimination status, sporadic outbreaks
- Examples: Measles, polio, rubella in countries with strong vaccination
- Frequency: Typically annual, quarterly, or monthly surveillance

❌ **Use default `mode='cumulative'` when:**
- Data reports **total cumulative cases**
- Cases **always increase** (or stay constant)
- Disease: Ongoing epidemic, endemic circulation
- Examples: COVID-19, seasonal flu, most OWID datasets
- Frequency: Daily, weekly observations

### Basic Workflow

```python
import pandas as pd
from epydemics import DataContainer, Model

# Example: Mexico measles (annual incident cases)
dates = pd.date_range('2010', periods=15, freq='YE')
data = pd.DataFrame({
    'I': [220, 55, 667, 164, 81,      # Incident cases (can vary)
          34, 12, 0, 0, 4,            # Near-elimination
          18, 45, 103, 67, 89],       # Reintroduction
    'D': [1, 1, 3, 4, 4, ...],        # Cumulative deaths
    'N': [120_000_000] * 15
}, index=dates)

# Create container with incidence mode
container = DataContainer(data, mode='incidence', window=3)

# Standard workflow (no changes!)
model = Model(container)
model.create_model()
model.fit_model(max_lag=3)
model.forecast(steps=5)
model.run_simulations(n_jobs=1)
model.generate_result()

# Results include both I and C
print(model.results['I'])  # Incident (can vary)
print(model.results['C'])  # Cumulative (monotonic)
```

### How It Works

1. **Data Processing:**
   - Incidence mode: `I` preserved, `C = cumsum(I)` generated
   - Cumulative mode: `C` preserved, `I = diff(C)` generated

2. **Feature Engineering:**
   - Same SIRD compartments for both modes
   - Same rate formulas: `alpha`, `beta`, `gamma`
   - Same VAR forecasting approach

3. **Mode Propagation:**
   ```python
   container = DataContainer(data, mode='incidence')
   model = Model(container)  
   print(model.mode)  # → 'incidence' (auto-inherited)
   ```

### Example: Measles Outbreak Cycles

```python
# Elimination → reintroduction pattern
incident_cases = np.array([
    220, 55, 667, 164, 81,   # Sporadic
    34, 12, 0, 0, 4,         # Elimination
    18, 45, 103, 67, 89      # Reintroduction
])

container = DataContainer(data, mode='incidence')

# I can decrease to zero (elimination achieved)
print("Elimination years:", (container.data['I'] == 0).sum())

# But C is always monotonic
print("C monotonic:", all(container.data['C'].diff() >= 0))
```

### See Also

- **Notebook**: `examples/notebooks/07_incidence_mode_measles.ipynb`
- **Tests**: `tests/integration/test_incidence_mode_workflow.py`

---

## Looking Ahead: v0.10.0+

Future enhancements may include:
- Custom frequency parameters
- Frequency-specific rate calculations
- Native annual/monthly model fitting

---

## Additional Resources

- **Developer Documentation**: See `CLAUDE.md` for internal architecture
- **API Reference**: See `docs/API_AUDIT.md`
- **Examples**: Check `examples/notebooks/` for complete workflows
- **Issues**: Report problems at https://github.com/julihocc/epydemics/issues

---

**Questions?** Open an issue or check the examples in `examples/notebooks/`.

**Contributing?** See `CONTRIBUTING.md` for development guidelines.
