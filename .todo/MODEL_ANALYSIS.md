# Model Class Analysis

## Class Overview

The Model class implements a sophisticated epidemiological forecasting system that combines SIRD mathematical models with VAR (Vector Autoregression) time series analysis. It models time-varying infection, recovery, and mortality rates using logit-transformed rates.

## Current Structure

### Constructor and Attributes
```python
def __init__(self, data_container, start=None, stop=None, days_to_forecast=None):
    # Data management
    self.data_container = data_container
    self.window = data_container.window
    self.data = None

    # Time parameters
    self.start = start
    self.stop = stop
    self.days_to_forecast = days_to_forecast

    # Model components
    self.logit_ratios_model = None
    self.logit_ratios_model_fitted = None
    self.logit_ratios_values = None

    # Forecasting results
    self.forecasting_box = None
    self.forecasted_logit_ratios_tuple_arrays = None
    self.forecasting_interval = None
    self.forecast_index_start = None
    self.forecast_index_stop = None

    # Simulation results
    self.simulation = None
    self.results = None
```

## Key Methods and Functionality

### 1. VAR Model Management
- **create_logit_ratios_model()** - Creates VAR model on logit-transformed rates
- **fit_logit_ratios_model()** - Fits VAR model and sets forecast horizon
- **forecast_logit_ratios()** - Generates VAR forecasts with confidence intervals

### 2. SIRD Simulation Engine
- **simulate_for_given_levels()** - Runs SIRD simulation for specific rate scenarios
- **create_simulation_box()** - Creates nested Box structure for 27 scenarios (3x3x3)
- **run_simulations()** - Executes all 27 simulation scenarios

### 3. Results Processing
- **create_results_dataframe()** - Aggregates simulation results with central tendencies
- **generate_result()** - Creates complete results for all SIRD compartments

### 4. Visualization and Evaluation
- **visualize_results()** - Plots forecasts with uncertainty bands and actual data
- **evaluate_forecast()** - Computes MAE, MSE, RMSE, MAPE, SMAPE metrics

## Dependencies

### External Libraries
- **statsmodels.tsa.api.VAR** - Vector Autoregression modeling
- **python-box.Box** - Nested result containers
- **itertools.product** - Cartesian product for scenario combinations
- **matplotlib.pyplot** - Visualization
- **scikit-learn metrics** - Forecast evaluation
- **scipy.stats** - Statistical functions (gmean, hmean)
- **numpy** - Mathematical operations
- **pandas** - Data manipulation

### Internal Dependencies
- **reindex_data()** - Data reindexing function
- **logistic_function()** - Inverse logit transformation
- **Constants**: logit_ratios, forecasting_levels, compartments, central_tendency_methods
- **Visualization constants**: method_names, method_colors, compartment_labels

## Mathematical Foundation

### SIRD Discrete Model
```
S(t+1) = S(t) - I(t) * α(t) * S(t) / A(t)
I(t+1) = I(t) + I(t) * α(t) * S(t) / A(t) - β(t) * I(t) - γ(t) * I(t)
R(t+1) = R(t) + β(t) * I(t)
D(t+1) = D(t) + γ(t) * I(t)
```

### Rate Modeling
- Rates α, β, γ are logit-transformed for VAR modeling
- VAR provides forecasts with confidence intervals (lower, point, upper)
- 27 scenarios combine all confidence level combinations
- Results aggregated using mean, median, gmean, hmean

## Extraction Strategy

### New Module Structure
```
epydemics/models/
├── __init__.py
├── base.py           # BaseModel, SIRDModelMixin
├── sird.py           # SIRDModel class (main implementation)
├── var_forecasting.py # VAR-specific forecasting logic
└── simulation.py     # SIRD simulation engine
```

### Key Challenges
1. **Complex State Management** - Many interconnected attributes
2. **Box Dependencies** - Nested result structures
3. **Visualization Integration** - matplotlib plotting logic
4. **Multiple Responsibilities** - VAR modeling + SIRD simulation + visualization

### Proposed Refactoring
1. **Separate Concerns** - Split VAR modeling from SIRD simulation
2. **Interface Abstraction** - Use BaseModel for common patterns
3. **Composition over Inheritance** - VAR forecaster as component
4. **Result Objects** - Typed result containers instead of Box

## Testing Requirements

### Core Functionality Tests
1. **Model Creation and Fitting**
   - VAR model initialization with logit rates
   - Model fitting with different parameters
   - Error handling for invalid data

2. **Forecasting Tests**
   - Forecast generation with confidence intervals
   - Date range handling and indexing
   - Logit to probability transformations

3. **SIRD Simulation Tests**
   - Single scenario simulation accuracy
   - All 27 scenarios execution
   - Compartment conservation laws
   - Edge cases (zero values, boundary conditions)

4. **Results Processing Tests**
   - Central tendency calculations
   - Results dataframe structure
   - Box object navigation

5. **Visualization Tests**
   - Plot generation without errors
   - Correct data plotting
   - Legend and label accuracy

6. **Evaluation Tests**
   - Metric calculations (MAE, RMSE, etc.)
   - JSON export functionality
   - Comparison against known results

### Integration Tests
1. **End-to-End Workflow**
   - DataContainer -> Model -> Results pipeline
   - Real data processing
   - Performance benchmarks

2. **Backward Compatibility**
   - Existing API preservation
   - Result format consistency
   - Parameter compatibility

## Implementation Notes

### Phase 1: Core Extraction
- Extract main Model class to models/sird.py
- Implement BaseModel interface
- Maintain exact API compatibility
- Move visualization constants to appropriate module

### Phase 2: Refactoring
- Separate VAR forecasting logic
- Extract simulation engine
- Improve error handling and type safety
- Add comprehensive documentation

### Phase 3: Enhancement
- Optional result caching
- Parallel simulation execution
- Advanced visualization options
- Model comparison utilities
