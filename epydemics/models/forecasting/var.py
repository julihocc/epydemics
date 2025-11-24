"""
Vector Autoregression (VAR) forecasting implementation.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR


class VARForecaster:
    """
    Wrapper around statsmodels VAR for epidemiological rate forecasting.
    
    This class handles the creation, fitting, and forecasting of Vector
    Autoregression models specifically designed for multivariate time series
    of epidemiological rates (or their transforms).
    """

    def __init__(self, data: Union[pd.DataFrame, np.ndarray]):
        """
        Initialize the VAR forecaster.

        Args:
            data: DataFrame or numpy array containing the multivariate time series to model.
                  Rows are time steps, columns are variables.
        """
        self.data = data
        self.model: Optional[VAR] = None
        self.fitted_model: Optional[Any] = None
        self.k_ar: int = 0

    def create_model(self, *args, **kwargs) -> None:
        """
        Create the underlying VAR model.

        Args:
            *args: Positional arguments for VAR constructor
            **kwargs: Keyword arguments for VAR constructor
        """
        # statsmodels VAR handles both array and dataframe, but usually expects array-like
        # If it's a DataFrame, .values extracts the numpy array.
        # If it's already an array, we use it directly.
        data_values = self.data.values if isinstance(self.data, pd.DataFrame) else self.data
        self.model = VAR(data_values, *args, **kwargs)

    def fit(self, *args, **kwargs) -> None:
        """
        Fit the VAR model.

        Args:
            *args: Positional arguments for fit()
            **kwargs: Keyword arguments for fit()
        """
        if self.model is None:
            self.create_model()
            
        self.fitted_model = self.model.fit(*args, **kwargs)
        self.k_ar = self.fitted_model.k_ar

    def forecast_interval(
        self, steps: int, **kwargs
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate point forecasts and confidence intervals.

        Args:
            steps: Number of steps to forecast
            **kwargs: Additional arguments for forecast_interval

        Returns:
            Tuple of (lower_bound, point_forecast, upper_bound) arrays
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before forecasting")
            
        data_values = self.data.values if isinstance(self.data, pd.DataFrame) else self.data
        return self.fitted_model.forecast_interval(
            data_values, steps, **kwargs
        )
