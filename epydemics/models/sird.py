"""SIRD epidemiological model with VAR time series forecasting."""

import logging
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from box import Box

from ..analysis.evaluation import evaluate_forecast as _evaluate_forecast
from ..analysis.visualization import visualize_results as _visualize_results
from ..core.constants import COMPARTMENTS, LOGIT_RATIOS
from ..data.preprocessing import reindex_data
from .base import BaseModel, SIRDModelMixin
from .var_forecasting import VARForecasting
from .simulation import EpidemicSimulation


class Model(BaseModel, SIRDModelMixin):
    """
    SIRD epidemiological model with VAR time series forecasting.

    This model implements the SIRD (Susceptible-Infected-Recovered-Deaths)
    compartmental model with time-varying rates modeled using Vector Autoregression
    on logit-transformed infection, recovery, and mortality rates.
    """

    def __init__(
        self,
        data_container,
        start: Optional[str] = None,
        stop: Optional[str] = None,
        days_to_forecast: Optional[int] = None,
    ):
        """
        Initialize the SIRD Model.

        Args:
            data_container: DataContainer instance with preprocessed data
            start: Start date for model training (YYYY-MM-DD format)
            stop: Stop date for model training (YYYY-MM-DD format)
            days_to_forecast: Number of days to forecast ahead
        """
        # Data and model attributes
        self.data: Optional[pd.DataFrame] = None
        self.data_container = data_container
        self.window = data_container.window
        self.start = start
        self.stop = stop

        # Model parameters
        self.days_to_forecast = days_to_forecast

        self.data = reindex_data(data_container.data, start, stop)
        self.logit_ratios_values = self.data[LOGIT_RATIOS].values

        # Forecasting component
        self.var_forecasting = VARForecasting(
            self.data, self.logit_ratios_values, self.window
        )
        if self.days_to_forecast:
            self.var_forecasting.days_to_forecast = self.days_to_forecast
        
        # Results and simulation attributes (set during model execution)
        self.results: Optional[Box] = None
        self.simulation_engine: Optional[EpidemicSimulation] = None

    @property
    def logit_ratios_model(self):
        """Get the underlying VAR model from the forecaster (for backward compatibility)."""
        return self.var_forecasting.logit_ratios_model

    @property
    def logit_ratios_model_fitted(self):
        """Get the fitted VAR model from the forecaster (for backward compatibility)."""
        return self.var_forecasting.logit_ratios_model_fitted

    def create_model(self, *args, **kwargs) -> None:
        """Create the VAR model for logit-transformed rates."""
        self.var_forecasting.create_logit_ratios_model(*args, **kwargs)

    def fit_model(self, *args, **kwargs) -> None:
        """Fit the VAR model to the data."""
        self.var_forecasting.fit_logit_ratios_model(*args, **kwargs)
        self.days_to_forecast = self.var_forecasting.days_to_forecast

    def forecast(self, steps: Optional[int] = None, **kwargs) -> None:
        """Generate forecasts for the specified number of steps."""
        self.var_forecasting.forecast_logit_ratios(steps, **kwargs)
        self.forecasting_box = self.var_forecasting.forecasting_box
        self.forecasting_interval = self.var_forecasting.forecasting_interval
        self.forecast_index_stop = self.var_forecasting.forecast_index_stop
        self.forecast_index_start = self.var_forecasting.forecast_index_start

        # Initialize simulation engine after forecasting is done
        self.simulation_engine = EpidemicSimulation(
            self.data, self.forecasting_box, self.forecasting_interval
        )

    def run_simulations(self) -> None:
        """Run epidemic simulations based on forecasted rates."""
        if self.simulation_engine is None:
            raise RuntimeError("Forecast must be generated before simulating epidemic.")
        self.simulation_engine.run_simulations()
        self.simulation = self.simulation_engine.simulation
        self.results = self.simulation_engine.results

    def generate_result(self) -> None:
        """Generate results for all compartments."""
        if self.simulation_engine is None:
            raise RuntimeError("Forecast and simulation must be generated before generating results.")
        self.simulation_engine.generate_result()
        self.results = self.simulation_engine.results

    def visualize_results(
        self,
        compartment_code: str,
        testing_data: Optional[pd.DataFrame] = None,
        log_response: bool = True,
    ) -> None:
        """
        Visualize forecast results for a specific compartment.

        Args:
            compartment_code: Compartment to visualize (A, C, S, I, R, D)
            testing_data: Optional test data for comparison
            log_response: Whether to use logarithmic scale
        """
        _visualize_results(
            results=self.results if self.results else self.simulation_engine.results,
            compartment_code=compartment_code,
            testing_data=testing_data,
            log_response=log_response,
        )

    def evaluate_forecast(
        self,
        testing_data: pd.DataFrame,
        compartment_codes: Tuple[str, ...] = ("C", "D", "I"),
        save_evaluation: bool = False,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate forecast performance against test data.

        Args:
            testing_data: DataFrame with actual values for comparison
            compartment_codes: Tuple of compartment codes to evaluate
            save_evaluation: Whether to save results to JSON file
            filename: Optional filename for saving (auto-generated if None)

        Returns:
            Dictionary with evaluation metrics for each compartment and method
        """
        return _evaluate_forecast(
            results=self.results if self.results else self.simulation_engine.results,
            testing_data=testing_data,
            compartment_codes=compartment_codes,
            save_evaluation=save_evaluation,
            filename=filename,
        )





