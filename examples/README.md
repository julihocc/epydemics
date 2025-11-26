# Epydemics Examples

This directory contains example notebooks demonstrating the capabilities of the epydemics library for epidemiological modeling and forecasting.

## Available Examples

### 1. Global COVID-19 Forecasting
**File:** `global_forecasting.ipynb`

The main research notebook demonstrating the adaptive forecasting methodology using time-varying SIRD model parameters. This notebook reproduces the results from "Adaptive Epidemic Forecasting Using Time Series Analysis and Machine Learning" (Castillo Colmenares, 2024).

**Features demonstrated:**
- Loading and preprocessing OWID global COVID-19 data
- Creating DataContainer with feature engineering
- Fitting VAR models to logit-transformed rates
- 30-day forecasting with uncertainty quantification
- 27-scenario Monte Carlo simulation
- Model evaluation with multiple metrics (MAE, MSE, RMSE, MAPE, SMAPE)
- Advanced visualization techniques
- R₀(t) calculation and interpretation

**Expected runtime:** 5-10 minutes
**Dataset:** Global COVID-19 data from Our World in Data

**Key results:**
- Confirmed cases forecast: MAPE = 4.27%
- Infected population forecast: MAPE = 25.98%
- Successfully captures multiple pandemic waves

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
