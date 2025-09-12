# DataContainer Class Analysis

## Class Overview

The DataContainer class is responsible for data preprocessing, validation, and feature engineering in the epydemics package. It transforms raw epidemiological data into a format suitable for SIRD modeling.

## Current Structure

### Constructor
```python
def __init__(self, raw_data, window=7):
    self.raw_data = raw_data
    self.window = window

    validate_data(self.raw_data)
    self.data = preprocess_data(self.raw_data)
    self.data = feature_engineering(self.data)
```

### Attributes
- `raw_data`: Original input data (pandas DataFrame)
- `window`: Rolling window size for smoothing (default: 7 days)
- `data`: Processed and engineered data with SIRD compartments

## Dependencies

### Functions Used
1. **validate_data(training_data)** - Line 73
   - Validates that input is a pandas DataFrame
   - Raises NotDataFrameError if not DataFrame

2. **preprocess_data(data, window=7)** - Line 123
   - Applies rolling window smoothing
   - Data cleaning and normalization

3. **feature_engineering(data)** - Line 172
   - Calculates SIRD compartments (S, I, R, D)
   - Computes differences (dC, dI, dR, dD)
   - Calculates rates (alpha, beta, gamma)
   - Applies logit transformations

### External Dependencies
- pandas (pd.DataFrame operations)
- logging (for debug messages)
- NotDataFrameError (from exceptions module)

## Data Transformation Pipeline

1. **Input**: Raw OWID-format data with columns ['date', 'total_cases', 'total_deaths', 'population']
2. **Validation**: Ensure DataFrame format
3. **Preprocessing**: Apply smoothing and cleaning
4. **Feature Engineering**: Calculate SIRD compartments and rates
5. **Output**: Enriched DataFrame with all epidemiological features

## Key Features

### SIRD Compartments
- **S**: Susceptible population
- **I**: Infected (active cases)
- **R**: Recovered cases
- **D**: Deaths
- **C**: Cumulative cases
- **A**: Total population

### Rate Calculations
- **alpha**: Infection rate α(t) = (S(t)+I(t))/(S(t)I(t)) * ΔC(t)
- **beta**: Recovery rate β(t) = ΔR(t)/I(t)
- **gamma**: Mortality rate γ(t) = ΔD(t)/I(t)

### Logit Transformations
- logit_alpha, logit_beta, logit_gamma for VAR modeling

## Extraction Strategy

### New Module Structure
```
epydemics/data/
├── __init__.py
├── container.py       # DataContainer class
├── validation.py      # validate_data function
├── preprocessing.py   # preprocess_data function
└── features.py        # feature_engineering function
```

### Testing Requirements
1. **Input Validation Tests**
   - Test with valid DataFrame
   - Test with invalid inputs (non-DataFrame)
   - Test with missing columns

2. **Data Processing Tests**
   - Test window parameter effects
   - Test with different data sizes
   - Test smoothing operations

3. **Feature Engineering Tests**
   - Test SIRD calculations
   - Test rate computations
   - Test logit transformations
   - Test edge cases (zero values)

4. **Integration Tests**
   - Test full pipeline with sample data
   - Test backward compatibility
   - Test performance benchmarks

## Implementation Notes

- Maintain exact same API for backward compatibility
- Add comprehensive type hints
- Include detailed docstrings
- Handle edge cases robustly
- Preserve logging behavior
- Maintain dependency on constants module
