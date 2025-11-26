"""SIRD epidemiological model with VAR time series forecasting."""

import logging
import warnings
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from box import Box

from ..analysis.evaluation import evaluate_forecast as _evaluate_forecast
from ..analysis.visualization import visualize_results as _visualize_results
from ..core.constants import COMPARTMENTS, FORECASTING_LEVELS, LOGIT_RATIOS
from ..data.preprocessing import reindex_data
from .base import BaseModel, SIRDModelMixin
from .var_forecasting import VARForecasting
from .simulation import EpidemicSimulation


from epydemics.core.config import get_settings


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
        self.var_forecasting.create_logit_ratios_model()

    def create_logit_ratios_model(self, *args, **kwargs) -> None:
        """DEPRECATED: Use create_model() instead.

        This method is deprecated and will be removed in v0.8.0.
        Use create_model() for the same functionality.
        """
        warnings.warn(
            "create_logit_ratios_model() is deprecated and will be removed in v0.8.0. "
            "Use create_model() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.create_model(*args, **kwargs)

    def fit_model(self, *args, **kwargs) -> None:
        """Fit the VAR model to the data."""
        settings = get_settings()
        kwargs.setdefault("max_lag", settings.VAR_MAX_LAG)
        kwargs.setdefault("ic", settings.VAR_CRITERION)
        self.var_forecasting.fit_logit_ratios_model(*args, **kwargs)
        self.days_to_forecast = self.var_forecasting.days_to_forecast

    def fit_logit_ratios_model(self, *args, **kwargs) -> None:
        """DEPRECATED: Use fit_model() instead.

        This method is deprecated and will be removed in v0.8.0.
        Use fit_model() for the same functionality.
        """
        warnings.warn(
            "fit_logit_ratios_model() is deprecated and will be removed in v0.8.0. "
            "Use fit_model() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.fit_model(*args, **kwargs)

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

    def forecast_logit_ratios(self, steps: Optional[int] = None, **kwargs) -> None:
        """DEPRECATED: Use forecast() instead.

        This method is deprecated and will be removed in v0.8.0.
        Use forecast() for the same functionality.
        """
        warnings.warn(
            "forecast_logit_ratios() is deprecated and will be removed in v0.8.0. "
            "Use forecast() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.forecast(steps, **kwargs)

    def run_simulations(self, n_jobs: Optional[int] = None) -> None:
        """
        Run epidemic simulations based on forecasted rates.

        This method supports both sequential and parallel execution modes for improved performance.

        Args:
            n_jobs: Number of parallel jobs to use:
                - None: Use config default (auto-detect CPU count if PARALLEL_SIMULATIONS=True)
                - 1: Sequential execution
                - >1: Parallel execution with specified number of workers

        Raises:
            RuntimeError: If forecast has not been generated yet
            ValueError: If n_jobs < 1

        Examples:
            >>> model.run_simulations()  # Use config default
            >>> model.run_simulations(n_jobs=1)  # Force sequential
            >>> model.run_simulations(n_jobs=4)  # Use 4 parallel workers
        """
        if self.simulation_engine is None:
            raise RuntimeError("Forecast must be generated before simulating epidemic.")
        self.simulation_engine.run_simulations(n_jobs=n_jobs)
        self.simulation = self.simulation_engine.simulation
        self.results = self.simulation_engine.results

    def generate_result(self) -> None:
        """Generate results for all compartments."""
        if self.simulation_engine is None:
            raise RuntimeError(
                "Forecast and simulation must be generated before generating results."
            )
        self.simulation_engine.generate_result()
        self.results = self.simulation_engine.results

    def calculate_R0(self) -> pd.Series:
        """Calculate basic reproduction number R₀(t) = α(t) / (β(t) + γ(t)).

        The basic reproduction number R₀ represents the average number of secondary
        infections caused by a single infected individual in a completely susceptible
        population. It is a critical epidemiological metric for understanding epidemic
        dynamics:
        - R₀ > 1: Epidemic grows (each infected person infects more than one other)
        - R₀ = 1: Critical threshold (epidemic remains stable)
        - R₀ < 1: Epidemic declines (insufficient transmission to sustain spread)

        Returns:
            pd.Series: Time series of R₀ values indexed by date

        Raises:
            ValueError: If required rate columns are not present in data

        Examples:
            >>> model = Model(container, start="2020-03-01", stop="2020-12-31")
            >>> R0 = model.calculate_R0()
            >>> print(f"Mean R₀: {R0.mean():.2f}")
            Mean R₀: 1.85
            >>> print(f"R₀ > 1 for {(R0 > 1).sum()} days")
            R₀ > 1 for 245 days

        Notes:
            - Calculated from historical data rates (alpha, beta, gamma)
            - Use forecast_R0() for forecasted reproduction numbers
            - High variability in R₀ reflects changing interventions and behavior
        """
        required_cols = ["alpha", "beta", "gamma"]
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        if missing_cols:
            raise ValueError(
                f"Missing required columns for R₀ calculation: {missing_cols}"
            )

        alpha = self.data["alpha"]
        beta = self.data["beta"]
        gamma = self.data["gamma"]

        R0 = alpha / (beta + gamma)
        R0.name = "R0"

        return R0

    def forecast_R0(self) -> pd.DataFrame:
        """Calculate R₀(t) for forecasted parameters across all scenarios.

        Generates basic reproduction number forecasts by combining forecasted
        infection rates (α) with recovery (β) and mortality (γ) rates across
        all 27 scenario combinations (3 confidence levels × 3 rates).

        Returns:
            pd.DataFrame: R₀ values for each scenario combination.
                Columns are named as "alpha_level|beta_level|gamma_level"
                (e.g., "lower|point|upper"). Index is the forecasting interval.

        Raises:
            ValueError: If forecast has not been generated yet

        Examples:
            >>> model = Model(container, start="2020-03-01", stop="2020-12-31")
            >>> model.create_logit_ratios_model()
            >>> model.fit_logit_ratios_model()
            >>> model.forecast_logit_ratios(steps=30)
            >>> R0_forecast = model.forecast_R0()
            >>> print(R0_forecast.shape)
            (30, 27)
            >>> # Get mean R₀ across all scenarios
            >>> mean_R0 = R0_forecast.mean(axis=1)
            >>> print(f"Average forecasted R₀: {mean_R0.mean():.2f}")
            Average forecasted R₀: 1.15

        Notes:
            - Requires forecast_logit_ratios() to be called first
            - Each column represents a different scenario combination
            - Use mean(axis=1) to get average R₀ across scenarios
            - Uncertainty in R₀ reflects uncertainty in underlying rates
        """
        if not hasattr(self, "forecasting_box") or self.forecasting_box is None:
            raise ValueError(
                "Forecast must be generated before calculating R₀. "
                "Call forecast_logit_ratios() first."
            )

        R0_forecasts = {}

        for alpha_level in FORECASTING_LEVELS:
            for beta_level in FORECASTING_LEVELS:
                for gamma_level in FORECASTING_LEVELS:
                    alpha = self.forecasting_box["alpha"][alpha_level]
                    beta = self.forecasting_box["beta"][beta_level]
                    gamma = self.forecasting_box["gamma"][gamma_level]

                    scenario = f"{alpha_level}|{beta_level}|{gamma_level}"
                    R0_forecasts[scenario] = alpha / (beta + gamma)

        result = pd.DataFrame(R0_forecasts, index=self.forecasting_interval)

        # Calculate summary statistics from scenario columns only
        scenario_data = result.copy()  # Preserve original scenario-only data
        result["mean"] = scenario_data.mean(axis=1)
        result["median"] = scenario_data.median(axis=1)
        result["std"] = scenario_data.std(axis=1)
        result["min"] = scenario_data.min(axis=1)
        result["max"] = scenario_data.max(axis=1)

        return result

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
