# Changelog

All notable changes to the epydemics project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
