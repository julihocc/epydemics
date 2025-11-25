"""
Vector Autoregression (VAR) forecasting implementation.
"""
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, Tuple

from ..core.constants import FORECASTING_LEVELS, LOGIT_RATIOS
from ..utils.transformations import logistic_function
from .forecasting.var import VARForecaster


class VARForecasting:
    """
    Encapsulates the VAR forecasting logic extracted from the Model class.
    """

    def __init__(self, data: pd.DataFrame, logit_ratios_values: np.ndarray, window: int):
        self.data = data
        self.logit_ratios_values = logit_ratios_values
        self.window = window

        self.forecaster: Optional[VARForecaster] = None
        self.forecasted_logit_ratios: Optional[pd.DataFrame] = None
        self.forecasted_logit_ratios_tuple_arrays: Optional[Any] = None
        self.forecasting_interval: Optional[pd.DatetimeIndex] = None
        self.forecast_index_stop: Optional[pd.Timestamp] = None
        self.forecast_index_start: Optional[pd.Timestamp] = None
        self.days_to_forecast: Optional[int] = None
        self.forecasting_box: Optional[Dict[str, pd.DataFrame]] = None

    @property
    def logit_ratios_model(self):
        """Get the underlying VAR model from the forecaster (for backward compatibility)."""
        return self.forecaster.model if self.forecaster else None

    @property
    def logit_ratios_model_fitted(self):
        """Get the fitted VAR model from the forecaster (for backward compatibility)."""
        return self.forecaster.fitted_model if self.forecaster else None

    def create_logit_ratios_model(self, *args, **kwargs) -> None:
        """
        Create VAR model for logit-transformed rates.

        Args:
            *args: Positional arguments for VAR constructor
            **kwargs: Keyword arguments for VAR constructor
        """
        self.forecaster = VARForecaster(self.logit_ratios_values)
        self.forecaster.create_model(*args, **kwargs)

    def fit_logit_ratios_model(self, *args, **kwargs) -> None:
        """
        Fit the VAR model to logit-transformed rates.

        Args:
            *args: Positional arguments for VAR.fit()
            **kwargs: Keyword arguments for VAR.fit()
        """
        if self.forecaster is None:
            self.create_logit_ratios_model()
            
        self.forecaster.fit(*args, **kwargs)
        
        if self.days_to_forecast is None:
            self.days_to_forecast = self.forecaster.k_ar + self.window

    def forecast_logit_ratios(self, steps: Optional[int] = None, **kwargs) -> None:
        """
        Generate forecasts for logit-transformed rates.

        Args:
            steps: Number of steps to forecast (overrides days_to_forecast)
            **kwargs: Keyword arguments for forecast_interval()
        """
        if steps:
            self.days_to_forecast = steps
        last_date = self.data.index[-1]
        self.forecast_index_start = last_date + pd.Timedelta(days=1)
        self.forecast_index_stop = last_date + pd.Timedelta(days=self.days_to_forecast)
        self.forecasting_interval = pd.date_range(
            start=self.forecast_index_start,
            end=self.forecast_index_stop,
            freq="D",
        )
        try:
            self.forecasted_logit_ratios_tuple_arrays = (
                self.forecaster.forecast_interval(
                    self.days_to_forecast, **kwargs
                )
            )
        except Exception as e:
            raise Exception(e)

        self.forecasting_box = {
            LOGIT_RATIOS[0]: pd.DataFrame(
                self.forecasted_logit_ratios_tuple_arrays[0],
                index=self.forecasting_interval,
                columns=FORECASTING_LEVELS,
            ),
            LOGIT_RATIOS[1]: pd.DataFrame(
                self.forecasted_logit_ratios_tuple_arrays[1],
                index=self.forecasting_interval,
                columns=FORECASTING_LEVELS,
            ),
            LOGIT_RATIOS[2]: pd.DataFrame(
                self.forecasted_logit_ratios_tuple_arrays[2],
                index=self.forecasting_interval,
                columns=FORECASTING_LEVELS,
            ),
        }

        self.forecasting_box["alpha"] = self.forecasting_box["logit_alpha"].apply(
            logistic_function
        )
        self.forecasting_box["beta"] = self.forecasting_box["logit_beta"].apply(
            logistic_function
        )
        self.forecasting_box["gamma"] = self.forecasting_box["logit_gamma"].apply(
            logistic_function
        )
