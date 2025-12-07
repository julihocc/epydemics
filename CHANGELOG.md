# Changelog

All notable changes to the epydemics project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2025-12-07

### Added - Phase 1: Multi-Frequency Support & Annual Data Workarounds

**Core Features:**
- **Frequency Detection System** (`src/epydemics/data/preprocessing.py`)
  - `detect_frequency()`: Automatic detection of D/W/M/Y frequencies from date index
  - Robust handling of different date ranges (minimum 2 points)
  - Tolerance-based frequency classification
  - Returns standardized frequency codes (D, W, M, Y)
  
- **Frequency Mismatch Warning System**
  - `warn_frequency_mismatch()`: Clear warnings when reindexing between frequencies
  - Actionable recommendations for users (use temporal aggregation, wait for v0.9.0)
  - Explains limitations of annual→daily reindexing (forward-fill artifacts)
  - Can be suppressed when limitations are understood
  
- **Temporal Aggregation** (`Model.aggregate_forecast()`)
  - Aggregate daily forecasts to annual/monthly/weekly output
  - Multiple aggregation functions: sum, mean, last, max, min
  - Support for Y/M/W target frequencies
  - Preserves confidence intervals from all simulation scenarios
  - Custom central tendency methods (mean, median)
  - Returns DataFrame with aggregated forecasts
  
- **Modern Pandas Compatibility**
  - Added `MODERN_FREQUENCY_ALIASES` constant mapping deprecated to modern aliases
  - Y → YE (year-end), M → ME (month-end)
  - Eliminates FutureWarnings from pandas 2.2+
  - Applied throughout codebase (tests, fixtures, examples)

**New Constants** (`src/epydemics/core/constants.py`):
- `SUPPORTED_FREQUENCIES = ["D", "W", "M", "Y", "A"]`
- `DEFAULT_FREQUENCY = "D"`
- `FREQUENCY_ALIASES` - user-friendly names mapping
- `RECOVERY_LAG_BY_FREQUENCY` - frequency-specific lag values
- `MODERN_FREQUENCY_ALIASES` - pandas 2.2+ compatible aliases

**Testing Infrastructure:**
- 45 new tests for frequency detection, temporal aggregation, and annual workflows
- 18 unit tests for frequency detection (`test_frequency_detection.py`)
- 18 unit tests for temporal aggregation (`test_temporal_aggregation.py`)
- 11 integration tests for complete annual workflow (`test_annual_workflow_v080.py`)
- Enhanced backward compatibility tests (5 new tests)
- All 291 existing tests pass without modification (100% backward compatible)

**Documentation:**
- **NEW: `docs/USER_GUIDE.md`** (407 lines)
  - When to use/not use epydemics
  - Data preparation guide (cumulative vs incidence)
  - Multi-frequency support documentation
  - Annual surveillance data workaround (Phase 1)
  - Best practices and troubleshooting
  - v0.9.0 migration preview
  
- **NEW: Example Notebook** (`examples/notebooks/06_annual_measles_workaround.ipynb`)
  - Complete 10-section guide to annual data workflow
  - Realistic USA measles simulation (1980-2020)
  - Demonstrates frequency detection, warnings, aggregation
  - Comparison with COVID-19 workflow
  - Visualization of limitations (reindexing artifacts)
  - v0.9.0 native support preview

- **Updated: `README.md`**
  - Version 0.8.0 features highlighted
  - Prominent link to USER_GUIDE.md
  - Annual data warning box
  - Reorganized documentation links
  - Updated "Further work" section

- **Updated: `CLAUDE.md`** (Developer documentation)
  - Annual Surveillance Data Support section (150+ lines)
  - Temporal aggregation patterns
  - Phase 1 workaround guidance
  - v0.9.0 roadmap

### Changed

**API Enhancements:**
- `Model.aggregate_forecast()` - New method for temporal aggregation
  - Parameters: `compartment_code`, `target_frequency`, `aggregate_func`, `methods`
  - Returns aggregated DataFrame with scenarios and central tendencies
  
- `reindex_data()` - Enhanced with frequency detection
  - Automatically detects source frequency
  - Emits warnings for frequency mismatches
  - Uses modern pandas frequency aliases internally
  
**Internal Improvements:**
- Updated all date range generation to use YE/ME instead of deprecated Y/M
- Enhanced `DataContainer` to support annual data with warnings
- Modified `Model` to handle sparse annual data (lower default lags)
- Improved test fixtures for multiple frequencies

### Fixed

- Eliminated all pandas FutureWarnings about deprecated frequency aliases
- Fixed frequency detection for edge cases (2-point datasets, irregular spacing)
- Corrected docstring examples to use modern frequency codes
- Updated test fixtures to use YE/ME frequency aliases

### Dependencies

- No new dependencies required
- Compatible with pandas >= 2.0 (modern frequency aliases)
- Compatible with existing Python 3.9+ environments

### Migration Guide

**From v0.7.0 to v0.8.0:**

All existing code continues to work without changes. New features are opt-in.

**For Annual Data Users:**
```python
# Old approach (would fail or give poor results)
container = DataContainer(annual_data, window=7)  # Not recommended

# New v0.8.0 approach (Phase 1 workaround)
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message=".*FREQUENCY MISMATCH.*")
    container = DataContainer(annual_data, window=1)

model = Model(container, start="1982", stop="2010")
model.create_model()
model.fit_model(max_lag=3)
model.forecast(steps=365 * 10)  # 10 years in days
model.run_simulations(n_jobs=1)
model.generate_result()

# Aggregate to annual output
annual_forecast = model.aggregate_forecast(
    "C", target_frequency="Y", aggregate_func="last", methods=["mean", "median"]
)
```

**Looking Ahead to v0.9.0:**
Phase 2 will bring native multi-frequency support:
```python
# Future v0.9.0 API (not available yet)
container = DataContainer(annual_data, frequency='Y', mode='incidence')
model = Model(container, start="1982", stop="2010")
model.forecast(steps=10)  # 10 years natively - no reindexing!
```

### Known Limitations

- Annual data is still reindexed to daily internally (forward-fill creates artifacts)
- Temporal aggregation is a workaround, not a true solution
- Annual workflow not recommended for production critical decisions
- Suitable for exploratory analysis and validation
- Native annual support planned for v0.9.0 (Q1 2026)

### Performance

- No performance regression on existing workflows
- Temporal aggregation adds < 100ms overhead
- Frequency detection is O(1) for typical datasets
- All optimizations from v0.7.0 maintained (parallel simulations, caching)

### Related Issues

- Closes #99: Implement frequency detection and warnings for annual data
- Closes #100: Add temporal aggregation to Model.forecast()
- Closes #101: Create USER_GUIDE.md and update documentation
- Closes #102: Create example notebook: Annual Measles Data Workaround
- Completes #98: [EPIC] Phase 1: Quick Wins - Measles Integration Support

### Contributors

- Juliho David Castillo Colmenares (@julihocc)

---

## [0.7.0] - 2025-11-28

### Added
- **SIRDV Vaccination Model**: Extended SIRD model with Vaccinated compartment (V) and vaccination rate (δ)
  - Automatic detection from vaccination data in OWID datasets
  - 81 simulation scenarios (3⁴ confidence levels for α, β, γ, δ)
  - Conservation law: N = S + I + R + D + V
  - 4D Box structure for simulation storage: `simulation[α][β][γ][δ]`
- **SIRDV Data Pipeline** (16 new tests)
  - Vaccination compartment (V) feature engineering
  - Vaccination rate (δ = dV/S) calculation
  - Negative dV clipping to handle data anomalies
  - SIRDV conservation law validation
- **SIRDV VAR Forecasting** (15 new tests)
  - Dimension-agnostic VAR forecaster supporting 3 or 4 rates
  - Logit transformation for delta rate
  - Dynamic rate detection from available logit columns
- **SIRDV Simulation Engine** (13 new tests)
  - Vaccination flow dynamics: `vaccination = δ * S`
  - Updated susceptible equation: `new_S = S - infection - vaccination`
  - 81 scenario generation for SIRDV vs 27 for SIRD
  - Parallel execution support for SIRDV simulations
- **SIRDV Model Integration** (10 new tests)
  - Automatic `has_vaccination` flag detection
  - Cache key differentiation between SIRD and SIRDV
  - Results generation including V compartment
- **SIRDV Visualization & Evaluation** (10 new tests)
  - V compartment plotting with "Vaccinated" label
  - Evaluation metrics (MAE, MSE, RMSE, MAPE, SMAPE) for V
  - Full support for all 7 SIRDV compartments (S, I, R, D, V, C, A)

### Changed
- Updated `COMPARTMENTS` constant to include "V" (Vaccinated)
- Updated `RATIOS` constant to include "delta" (δ)
- Updated `LOGIT_RATIOS` constant to include "logit_delta"
- Updated `COMPARTMENT_LABELS` to include "V": "Vaccinated"
- Modified `feature_engineering()` to handle optional vaccination column
- Enhanced `VARForecasting` to support variable number of rates (3 or 4)
- Updated `EpidemicSimulation` to handle 3D (SIRD) or 4D (SIRDV) Box structures
- Modified `Model` class to detect and handle vaccination automatically

### Fixed
- VAR `forecast_interval` data structure parsing for 4-rate models
- Integration test parameters adjusted for 4-variable VAR estimation requirements

### Documentation
- Added SIRDV section to CLAUDE.md with mathematical formulation
- Updated README.md with SIRDV features and version bump to 0.7.0
- Enhanced copilot instructions with SIRDV implementation details

### Performance
- SIRDV simulations ~3x longer than SIRD due to 81 vs 27 scenarios
- Parallel execution (`n_jobs=None`) recommended for SIRDV
- SIRDV requires longer training periods or smaller max_lag for VAR estimation

### Backward Compatibility
- ✅ Full backward compatibility maintained with SIRD models
- ✅ All existing SIRD functionality unchanged
- ✅ Automatic fallback to SIRD when vaccination data unavailable
- ✅ 8 dedicated backward compatibility tests

### Testing
- Added 64 new SIRDV-specific tests
- Total test count: 192 tests passing
- Test categories:
  - 16 tests: SIRDV data pipeline
  - 15 tests: SIRDV VAR forecasting
  - 13 tests: SIRDV simulation engine
  - 10 tests: SIRDV model integration
  - 10 tests: SIRDV visualization & evaluation

## [0.6.1-dev] - Unreleased

### Added
- Result caching feature with file-based storage
- Configuration support via environment variables
- Cache key generation based on model parameters and data state

## [0.6.0] - Previous Release

### Added
- Extracted analysis module with visualization and evaluation functions
- Modern pandas syntax (deprecated methods replaced)
- Parallel simulation support with `n_jobs` parameter
- Professional formatting utilities for time axes

### Changed
- Modular architecture with separate analysis module
- Enhanced type safety and improved interfaces
- Comprehensive test coverage for analysis functionality

[0.7.0]: https://github.com/julihocc/epydemics/releases/tag/v0.7.0
[0.6.1-dev]: https://github.com/julihocc/epydemics/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/julihocc/epydemics/releases/tag/v0.6.0
