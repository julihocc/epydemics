# Epydemics: Forecasting COVID-19 using time series and machine learning

**Version 0.6.1-dev** - SIRDV Vaccination Support

`epydemics` is a Python library for epidemiological modeling and forecasting. It provides tools for creating, fitting, and evaluating discrete SIRD/SIRDV models with time-dependent parameters. The library is designed to be flexible and extensible, allowing users to easily incorporate their own data and models.

## Features

-   **Discrete SIRD/SIRDV Models**: Automatic detection and support for both:
    -   **SIRD**: Susceptible-Infected-Recovered-Deceased model
    -   **SIRDV**: SIRD with Vaccination compartment (automatically detected)
-   **Time Series Forecasting**: VAR (Vector Autoregression) models on logit-transformed rates with confidence intervals
-   **Parallel Simulation**: Multi-core support for faster Monte Carlo simulations (27 scenarios)
-   **Data Container**: A convenient class for loading, preprocessing, and storing epidemiological data from OWID
-   **Model Evaluation**: Comprehensive metrics (MAE, MSE, RMSE, MAPE, SMAPE) across multiple central tendencies
-   **Visualization**: Professional plotting functions with confidence bands and testing data overlay
-   **Result Caching**: Optional file-based caching to avoid recomputation

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

-   **[TUTORIAL.md](TUTORIAL.md)**: A step-by-step guide to using `epydemics` for COVID-19 forecasting.
-   **[ARCHITECTURE.md](ARCHITECTURE.md)**: A high-level overview of the project's architecture.
-   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Instructions for contributing to the project.

## Further work

Recent additions in v0.6.1-dev:
-   ✅ **SIRDV Model Support**: Automatic detection and modeling of vaccination data
-   ✅ **Parallel Simulations**: Multi-core execution for improved performance
-   ✅ **Result Caching**: Optional caching to avoid recomputation
-   ✅ **Enhanced Testing**: Comprehensive test coverage with slow test markers

Future directions:

-   **More advanced time series models**: The current version uses VAR models. More advanced approaches like SARIMAX, Prophet, or deep learning could improve accuracy.
-   **Support for other epidemiological models**: Extend to SEIR, SEIRD, or metapopulation models.
-   **Improved visualization**: Interactive dashboards and real-time updating plots.
-   **More comprehensive documentation**: Detailed SIRDV examples and case studies with real vaccination data.

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