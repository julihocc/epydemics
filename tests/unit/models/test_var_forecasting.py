"""
Unit tests for the VARForecasting class.
"""

import numpy as np
import pandas as pd
import pytest

from epydemics.data import DataContainer
from epydemics.models.var_forecasting import VARForecasting


class TestVARForecasting:
    """Test VARForecasting class functionality."""

    @pytest.fixture
    def sample_data_container(self):
        """Create sample DataContainer for testing."""
        dates = pd.date_range("2020-01-01", periods=50, freq="D")
        sample_data = pd.DataFrame(
            {
                "C": np.cumsum(np.random.poisson(10, 50)) + 100,
                "D": np.cumsum(np.random.poisson(1, 50)) + 1,
                "N": [1000000] * 50,
            },
            index=dates,
        )
        return DataContainer(sample_data, window=7)

    @pytest.fixture
    def var_forecasting_instance(self, sample_data_container):
        """Create a VARForecasting instance for testing."""
        data = sample_data_container.data
        logit_ratios_values = data[["logit_alpha", "logit_beta", "logit_gamma"]].values
        window = sample_data_container.window
        return VARForecasting(data, logit_ratios_values, window)

    def test_var_forecasting_init(self, var_forecasting_instance):
        """Test VARForecasting initialization."""
        assert var_forecasting_instance.data is not None
        assert var_forecasting_instance.logit_ratios_values is not None
        assert var_forecasting_instance.window == 7
        assert var_forecasting_instance.forecaster is None
        assert var_forecasting_instance.days_to_forecast is None

    def test_create_logit_ratios_model(self, var_forecasting_instance):
        """Test creation of the underlying VAR model."""
        var_forecasting_instance.create_logit_ratios_model()
        assert var_forecasting_instance.forecaster is not None
        assert var_forecasting_instance.forecaster.model is not None

    def test_fit_logit_ratios_model(self, var_forecasting_instance):
        """Test fitting of the VAR model."""
        var_forecasting_instance.create_logit_ratios_model()
        var_forecasting_instance.fit_logit_ratios_model()
        assert var_forecasting_instance.forecaster.fitted_model is not None
        assert var_forecasting_instance.days_to_forecast is not None
        assert var_forecasting_instance.days_to_forecast > 0

    def test_forecast_logit_ratios(self, var_forecasting_instance):
        """Test forecasting of logit ratios."""
        var_forecasting_instance.create_logit_ratios_model()
        var_forecasting_instance.fit_logit_ratios_model()
        var_forecasting_instance.forecast_logit_ratios(steps=5)

        assert var_forecasting_instance.forecasting_box is not None
        assert var_forecasting_instance.forecasting_interval is not None
        assert len(var_forecasting_instance.forecasting_interval) == 5

        for rate in ["alpha", "beta", "gamma", "logit_alpha", "logit_beta", "logit_gamma"]:
            assert rate in var_forecasting_instance.forecasting_box
