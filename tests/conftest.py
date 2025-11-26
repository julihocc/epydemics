"""Test configuration and fixtures."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_owid_data():
    """Sample OWID-format epidemiological data for testing."""
    dates = pd.date_range(start="2020-03-01", end="2020-03-31", freq="D")
    np.random.seed(42)  # Reproducible data

    # Simulate realistic epidemic data
    base_cases = np.cumsum(np.random.exponential(50, len(dates)))
    base_deaths = np.cumsum(np.random.exponential(2, len(dates)))

    data = pd.DataFrame(
        {
            "date": dates,
            "total_cases": base_cases,
            "total_deaths": base_deaths,
            "population": [1000000] * len(dates),
        }
    )

    return data


@pytest.fixture
def sample_processed_data():
    """Sample processed epidemiological data for testing."""
    dates = pd.date_range(start="2020-03-01", end="2020-03-31", freq="D")

    data = pd.DataFrame(
        {
            "C": np.cumsum(np.random.exponential(50, len(dates))),
            "D": np.cumsum(np.random.exponential(2, len(dates))),
            "N": [1000000] * len(dates),
        },
        index=dates,
    )

    return data


@pytest.fixture
def sample_data_container(sample_owid_data):
    """DataContainer instance with processed sample data."""
    from epydemics.data.container import DataContainer

    # Process the data similar to process_data_from_owid
    processed_data = sample_owid_data.copy()
    processed_data.set_index("date", inplace=True)
    processed_data.index = pd.DatetimeIndex(processed_data.index)
    processed_data.columns = ["C", "D", "N"]

    return DataContainer(processed_data)
