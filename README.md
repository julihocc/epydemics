# Epydemics: Forecasting COVID-19 using time series and machine learning

**Version 0.8.0** - Multi-Frequency Support & Annual Data Workarounds

`epydemics` is a Python library for epidemiological modeling and forecasting. It provides tools for creating, fitting, and evaluating discrete SIRD/SIRDV models with time-dependent parameters. The library is designed to be flexible and extensible, allowing users to easily incorporate their own data and models.

**📖 New Users?** Start with the **[User Guide](docs/USER_GUIDE.md)** to understand when and how to use epydemics.

## Features

-   **Discrete SIRD Model**: A discrete Susceptible-Infected-Recovered-Deceased (SIRD) model with time-dependent parameters.
-   **SIRDV Vaccination Model** (v0.7.0): Extended model including Vaccinated compartment (V) and vaccination rate (δ).
-   **Time Series Forecasting**: Use of VAR (Vector Autoregression) models to forecast epidemic rates with logit transformation.
-   **Multi-Frequency Support** (v0.8.0): Automatic frequency detection (daily/weekly/monthly/annual) with mismatch warnings.
-   **Temporal Aggregation** (v0.8.0): Aggregate daily forecasts to annual/monthly/weekly output frequencies.
-   **Data Container**: A convenient class for loading, preprocessing, and storing epidemiological data.
-   **Parallel Simulations**: Multi-core support for faster Monte Carlo simulations (27 scenarios for SIRD, 81 for SIRDV).
-   **Result Caching**: File-based caching to avoid recomputing identical analyses.
-   **Model Evaluation**: Tools for evaluating model performance with MAE, MSE, RMSE, MAPE, SMAPE metrics.
-   **Visualization**: Professional plotting functions for results and forecasts.

> **⚠️ Annual Surveillance Data**: v0.8.0 provides workarounds for annual data (e.g., measles) through temporal aggregation. Native annual support coming in v0.9.0. See [User Guide](docs/USER_GUIDE.md#annual-surveillance-data-workaround) for details.

## SIRDV Model (New in v0.7.0)

The SIRDV model extends the classical SIRD model by incorporating vaccination:

**Compartments:**
- S: Susceptible
- I: Infected (active cases)
- R: Recovered
- D: Deaths
- V: Vaccinated (new)

**Rates:**
- α: Infection rate
- β: Recovery rate
- γ: Mortality rate
- δ: Vaccination rate (new)

**Key Features:**
- Automatic detection from vaccination data
- 81 simulation scenarios (3⁴ confidence levels)
- Conservation law: N = S + I + R + D + V
- Parallel execution recommended for performance

## Getting Started

To get started with `epydemics`, we recommend following the tutorial in [TUTORIAL.md](TUTORIAL.md).

## Installation

You can install `epydemics` from PyPI:

```bash
pip install epydemics
```

To install the latest development version, you can clone this repository and install it in editable mode:

```bash
git clone https://github.com/julihocc/epydemics.git
cd epydemics
pip install -e .
```

## Documentation

-   **[User Guide](docs/USER_GUIDE.md)**: Complete guide on when to use epydemics, data preparation, and frequency handling.
-   **[TUTORIAL.md](TUTORIAL.md)**: A step-by-step guide to using `epydemics` for COVID-19 forecasting.
-   **[ARCHITECTURE.md](ARCHITECTURE.md)**: A high-level overview of the project's architecture.
-   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Instructions for contributing to the project.
-   **[CLAUDE.md](.github/copilot-instructions.md)**: Developer documentation and internal architecture.

## Further work

Recent additions in v0.8.0:
-   ✅ **Frequency Detection & Warnings**: Automatic detection of data frequency with warnings for mismatches
-   ✅ **Temporal Aggregation**: Aggregate daily forecasts to annual/monthly/weekly for reporting
-   ✅ **Annual Data Workarounds**: Phase 1 support for annual surveillance data (native support in v0.9.0)
-   ✅ **Modern Pandas Compatibility**: Updated to use YE/ME frequency aliases (no FutureWarnings)

Previous releases (v0.6.1-v0.7.0):
-   ✅ **SIRDV Model Support**: Automatic detection and modeling of vaccination data
-   ✅ **Parallel Simulations**: Multi-core execution for improved performance
-   ✅ **Result Caching**: Optional caching to avoid recomputation
-   ✅ **Enhanced Testing**: Comprehensive test coverage with slow test markers

Future directions (v0.9.0+):

-   **Native Multi-Frequency Support**: True annual/monthly/weekly modeling without reindexing
-   **Incidence-First Mode**: Direct modeling of incident cases (not just cumulative)
-   **Importation Modeling**: Handle external case introductions for eliminated diseases
-   **More advanced time series models**: SARIMAX, Prophet, or deep learning approaches
-   **Support for other epidemiological models**: Extend to SEIR, SEIRD, or metapopulation models
-   **Improved visualization**: Interactive dashboards and real-time updating plots

## References

**Allen u.a. 2008** Allen, L.J.S. ; Brauer, F. ; Driessche, P. van den ;
 Bauch, C.T. ; Wu, J. ; Castillo-Chavez, C. ; Earn, D. ; Feng, Z. ;
 Lewis, M.A. ; Li, J. u.a.: Mathematical Epidemiology. Springer Berlin
 Heidelberg, 2008 (Lecture Notes in Mathematics).– URL https://books.
 google.com/books?id=gcP5l1a22rQC.– ISBN 9783540789109

**Andrade u.a. 2021** Andrade, Marinho G. ; Achcar, Jorge A. ; Conce
icc˜ ao, Katiane S. ; Ravishanker, Nalini: Time Series Regression Models
 for COVID-19 Deaths. In: J. Data Sci 19 (2021), Nr. 2, S. 269–292

**Hawas 2020** Hawas, Mohamed: Generated time-series prediction data of
 COVID-19s daily infections in Brazil by using recurrent neural networks. In:
 Data in brief 32 (2020), S. 106175

**Maleki u.a. 2020** Maleki, Mohsen ; Mahmoudi, Mohammad R. ; Wraith,
 Darren ; Pho, Kim-Hung: Time series modelling to forecast the confirmed
 and recovered cases of COVID-19. In: Travel medicine and infectious disease
 37 (2020), S. 101742

**Martcheva 2015** Martcheva, M.: An Introduction to Mathematical Epi
demiology. Springer US, 2015 (Texts in Applied Mathematics).– URL https:
 //books.google.com/books?id=tt7HCgAAQBAJ.– ISBN 9781489976123

**Singh u.a. 2020** Singh, Vijander ; Poonia, Ramesh C. ; Kumar, Sandeep ;
 Dass, Pranav ; Agarwal, Pankaj ; Bhatnagar, Vaibhav ; Raja, Linesh:
 Prediction of COVID-19 coronavirus pandemic based on time series data
 using Support Vector Machine. In: Journal of Discrete Mathematical Sciences
 and Cryptography 23 (2020), Nr. 8, S. 1583–1597

**Wacker und Schluter 2020** Wacker, Benjamin; Schluter, Jan: Time
continuous and time-discrete SIR models revisited: theory and applications.
 In: Advances in Difference Equations 2020 (2020), Nr. 1, S. 1–44.– ISSN
 1687-1847.– URL https://doi.org/10.1186/s13662-020-02907-9