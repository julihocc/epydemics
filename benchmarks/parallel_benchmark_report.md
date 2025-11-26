# Parallel Simulation Benchmark Results

**Date**: 2025-11-26T13:08:02.211736
**System**: Windows-10-10.0.26220-SP0
**CPU Count**: 16
**Python Version**: 3.10.11

## Configuration

- Data points: 150
- Training data: 105
- Forecast steps: 30
- Scenarios: 27
- Trials per config: 3

## Results Summary

| n_jobs | Mode | Mean Time (s) | Std (s) | Speedup | Efficiency |
|--------|------|---------------|---------|---------|------------|
|      1 | sequential |         0.020 |   0.000 |    1.00x |     100.0% |
|      2 | parallel   |         2.418 |   0.095 |    0.01x |       0.4% |
|      4 | parallel   |         2.751 |   0.079 |    0.01x |       0.2% |
|      6 | parallel   |         3.308 |   0.079 |    0.01x |       0.1% |
|      8 | parallel   |         4.056 |   0.146 |    0.00x |       0.1% |
|     16 | parallel   |         7.196 |   0.259 |    0.00x |       0.0% |

## Analysis

- **Best configuration**: n_jobs=2
- **Maximum speedup**: 0.01x
- **Time saved**: -2.40s (-12065.8% reduction)
- **Efficiency**: 0.4%

Note: Efficiency is moderate (0.4%), suggesting overhead from process creation and data serialization.

## Recommendations

For production use:
- Use `n_jobs=2` for best performance on this system
- Expected speedup: ~0.0x over sequential execution
- Set `PARALLEL_SIMULATIONS=True` in config or .env
- Use `n_jobs=1` for debugging or when running many models simultaneously