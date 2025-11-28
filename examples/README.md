# Epydemics Examples

This directory contains example notebooks and scripts demonstrating the capabilities of the epydemics library for epidemiological modeling and forecasting.

**Version**: 0.7.0 (includes SIRDV vaccination model)

## Directory Structure

```
examples/
├── notebooks/          # Jupyter notebooks with complete workflows
├── data/              # Data storage (OWID COVID-19 datasets)
├── download_data.py   # Data download utility
└── README.md          # This file
```

## Available Notebooks

### 1. SIRD Basic Workflow
**File:** `notebooks/01_sird_basic_workflow.ipynb`

Introduction to the SIRD (Susceptible-Infected-Recovered-Deaths) model.

**Topics:**
- Loading COVID-19 data from OWID
- Creating a DataContainer with preprocessing
- Fitting VAR models to time-varying rates
- 30-day forecasting with uncertainty
- 27-scenario Monte Carlo simulation
- Visualization and evaluation
- Performance metrics (MAE, RMSE, MAPE, SMAPE)

**Expected runtime:** 3-5 minutes  
**Model type:** SIRD (3 rates: α, β, γ)  
**Scenarios:** 27 (3³)

---

### 2. SIRDV Vaccination Analysis ⭐ NEW in v0.7.0
**File:** `notebooks/02_sirdv_vaccination_analysis.ipynb`

Complete guide to the SIRDV model with vaccination support.

**Topics:**
- Loading data with vaccination information
- Automatic SIRDV detection
- 4-rate VAR forecasting (α, β, γ, δ)
- 81-scenario Monte Carlo simulation
- V (Vaccinated) compartment visualization
- SIRDV vs SIRD comparison
- Vaccination impact analysis
- Performance optimization tips

**Expected runtime:** 5-8 minutes  
**Model type:** SIRDV (4 rates: α, β, γ, δ)  
**Scenarios:** 81 (3⁴)  
**Data requirements:** Requires `people_vaccinated` column

---

### 3. Global COVID-19 Forecasting
**File:** `notebooks/03_global_covid19_forecasting.ipynb`

Advanced research notebook demonstrating adaptive forecasting methodology using time-varying SIRD model parameters. Reproduces results from "Adaptive Epidemic Forecasting Using Time Series Analysis and Machine Learning" (Castillo Colmenares, 2024).

**Features:**
- Global COVID-19 data analysis
- Advanced VAR model selection (AIC criterion)
- Multi-wave pandemic capture
- R₀(t) calculation and interpretation
- Professional visualization techniques
- Comprehensive model evaluation

**Expected runtime:** 8-12 minutes  
**Dataset:** Global COVID-19 data (OWID_WRL)

**Key results:**
- Confirmed cases forecast: MAPE = 4.27%
- Infected population forecast: MAPE = 25.98%
- Successfully captures multiple pandemic waves

---

### 4. Parallel Simulations Demo
**File:** `notebooks/04_parallel_simulations.ipynb`

Performance optimization using parallel execution.

**Topics:**
- Sequential vs parallel simulation comparison
- Multi-core execution with `n_jobs` parameter
- Performance benchmarking
- Speedup analysis (4-7x improvement)
- Memory usage considerations
- Best practices for large-scale simulations

**Expected runtime:** 5-10 minutes  
**Recommendation:** Use for SIRDV models (81 scenarios)

## Running the Examples

### Prerequisites
```bash
# Install epydemics with development dependencies
pip install -e ".[dev]"

# Or install from PyPI
pip install epydemics

# Install jupyter for running notebooks
pip install jupyter
```

### Launch Jupyter
```bash
cd examples
jupyter notebook
```

Then open any `.ipynb` file from the Jupyter interface.

### Running from Command Line
```bash
# Convert notebook to Python script and run
jupyter nbconvert --to script global_forecasting.ipynb
python global_forecasting.py
```

## Data Directory

The `data/` subdirectory is used for caching downloaded OWID data to speed up subsequent runs. This directory is ignored by git (via .gitignore) to avoid committing large CSV files.

### Network Issues

If you encounter network connectivity errors when running the notebooks:

1. **Download data manually**: Visit https://covid.ourworldindata.org/data/owid-covid-data.csv and save to `data/owid-covid-data.csv`

2. **Use the helper script** (when you have internet):
   ```bash
   python download_data.py
   ```

3. **Check the data README**: See `data/README.md` for detailed troubleshooting steps

The epydemics package will automatically use local data if available when network downloads fail.

## Planned Examples

Future notebooks to be added:

- **Regional Comparison** (`regional_comparison.ipynb`): Compare forecast performance across different countries
- **Alternative Models** (`alternative_forecasters.ipynb`): Using SARIMAX and other time series models
- **Custom Analysis** (`custom_analysis.ipynb`): Building custom analysis pipelines
- **Visualization Guide** (`visualization_guide.ipynb`): Advanced plotting and interpretation

## Contributing Examples

If you've created an interesting analysis using epydemics, consider contributing it as an example:

1. Ensure your notebook runs from start to finish without errors
2. Add markdown cells explaining the methodology
3. Include interpretation of results
4. Clear all outputs before committing (to keep repository size small)
5. Submit a pull request

## Support

For questions or issues:
- GitHub Issues: https://github.com/julihocc/epydemics/issues
- Documentation: https://github.com/julihocc/epydemics#readme
- PyPI: https://pypi.org/project/epydemics/

## Citation

If you use these examples in your research, please cite:

```bibtex
@software{epydemics2024,
  author = {Castillo Colmenares, Juliho David},
  title = {Epydemics: Adaptive Epidemic Forecasting Using Time Series Analysis},
  year = {2024},
  url = {https://github.com/julihocc/epydemics}
}
```
