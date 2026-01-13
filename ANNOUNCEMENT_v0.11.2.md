# Epydemics v0.11.2 Release Announcement

**Publication-Ready Reporting Tools with ModelReport Class**

We're excited to announce the release of **epydemics v0.11.2**, now available on PyPI with comprehensive documentation updates highlighting the new ModelReport reporting tools introduced in v0.11.1.

## 🎉 What's New

### ModelReport Class (v0.11.1 Feature)
Publication-ready analysis and reporting in one line of code:

```python
from epydemics.analysis import ModelReport

# Create comprehensive report
report = ModelReport(model.results, testing_data, compartments=['I', 'D'])

# Export to multiple formats
report.export_markdown("analysis.md", include_figure=True)
report.export_latex_table("table1.tex", "summary")
fig = report.plot_forecast_panel(dpi=600, save_path="forecast.png")
```

**Key Features:**
- 📊 **Automated Summary Statistics**: Mean, median, std, CV per compartment
- 📈 **Forecast Evaluation**: MAE, RMSE, MAPE, SMAPE metrics
- 📝 **Markdown Export**: One-line report generation with embedded figures
- 📄 **LaTeX Tables**: Publication-quality tables for academic papers
- 🖼️ **High-DPI Figures**: 300-600 DPI multi-panel visualizations
- 🔍 **Model Comparison**: Compare multiple models side-by-side

### CI/CD Improvements (v0.11.2)
- Fixed Python version matrix (quoted "3.10" to prevent YAML float truncation)
- All tests passing on Python 3.9, 3.10, 3.11, 3.12

## 📦 Installation

```bash
pip install epydemics==0.11.2
```

Or upgrade from previous versions:

```bash
pip install --upgrade epydemics
```

## 📖 Documentation & Examples

- **Complete Tutorial**: [examples/notebooks/07_reporting_and_publication.ipynb](https://github.com/julihocc/epydemics/blob/main/examples/notebooks/07_reporting_and_publication.ipynb)
- **User Guide**: [docs/USER_GUIDE.md](https://github.com/julihocc/epydemics/blob/main/docs/USER_GUIDE.md)
- **Reporting Guide**: [docs/REPORTING_GUIDE.md](https://github.com/julihocc/epydemics/blob/main/docs/REPORTING_GUIDE.md)
- **API Documentation**: Full docstrings in `epydemics.analysis.reporting`

## 🔧 Quick Start

```python
from epydemics import DataContainer, Model
from epydemics.analysis import ModelReport
import pandas as pd

# 1. Prepare data
data = pd.DataFrame({'I': [...], 'D': [...], 'N': [...]}, index=dates)
container = DataContainer(data, mode='cumulative', frequency='D')

# 2. Create and run model
model = Model(container)
model.create_model()
model.fit_model(max_lag=14)
model.forecast(steps=30)
model.run_simulations(n_jobs=None)
model.generate_result()

# 3. Generate publication-ready reports
report = ModelReport(model.results, test_data)
report.export_markdown("covid_analysis.md", include_figure=True)
report.export_latex_table("forecast_metrics.tex", "evaluation")
```

## 🆕 All v0.11.x Features

- ✨ **ModelReport** class for publication-ready analysis
- 📊 **Multi-format export**: Markdown, LaTeX, PNG (300-600 DPI)
- 🔢 **Automated metrics**: Summary stats and forecast accuracy
- 📈 **Model comparison** utilities
- 🐛 **CI/CD fixes**: Python version matrix corrected
- ✅ **All v0.10.0+ features**: Fractional recovery lag, native multi-frequency, parallel simulations

## 🔗 Links

- **PyPI**: https://pypi.org/project/epydemics/0.11.2/
- **GitHub**: https://github.com/julihocc/epydemics
- **GitHub Release**: https://github.com/julihocc/epydemics/releases/tag/v0.11.2
- **Changelog**: [CHANGELOG.md](https://github.com/julihocc/epydemics/blob/main/CHANGELOG.md)

## 🙏 Feedback

We'd love to hear from you! Please report issues or request features at:
https://github.com/julihocc/epydemics/issues

## 📝 Release Notes

See [CHANGELOG.md](https://github.com/julihocc/epydemics/blob/main/CHANGELOG.md) for detailed release notes and version history.

---

**Happy modeling!** 🎉

*Epydemics Development Team*
