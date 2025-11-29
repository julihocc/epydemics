"""SIRD epidemiological model with VAR time series forecasting."""

import logging
import warnings
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from box import Box
import hashlib
import json
from pathlib import Path

from ..analysis.evaluation import evaluate_forecast as _evaluate_forecast
from ..analysis.visualization import visualize_results as _visualize_results
from ..core.constants import COMPARTMENTS, FORECASTING_LEVELS, LOGIT_RATIOS
from ..data.preprocessing import reindex_data
from .base import BaseModel, SIRDModelMixin
from .var_forecasting import VARForecasting  # Keep for backward compat
from .forecasting.orchestrator import ForecastingOrchestrator
from .simulation import EpidemicSimulation


from epydemics.core.config import get_settings


# Import __version__ after full module initialization to avoid circular import
def _get_pkg_version() -> str:
    from epydemics import __version__

    return __version__


class Model(BaseModel, SIRDModelMixin):
    """
    SIRD epidemiological model with multi-backend time series forecasting.

    This model implements the SIRD (Susceptible-Infected-Recovered-Deaths)
    compartmental model with time-varying rates. Supports multiple forecasting
    backends: VAR (default), Prophet, ARIMA, and LSTM (stub).

    The forecasting backend is selected via the `forecaster` parameter, with
    backend-specific configuration passed through `forecaster_kwargs`.

    Examples:
        Default VAR backend (v0.7.0 behavior):

        >>> model = Model(container, start="2020-03-01", stop="2020-12-31")
        >>> model.create_model()
        >>> model.fit_model(max_lag=10)

        Prophet with seasonality:

        >>> model = Model(
        ...     container,
        ...     forecaster="prophet",
        ...     yearly_seasonality=True,
        ...     changepoint_prior_scale=0.1
        ... )
        >>> model.create_model()
        >>> model.fit_model()

        Auto-ARIMA:

        >>> model = Model(
        ...     container,
        ...     forecaster="arima",
        ...     max_p=5,
        ...     seasonal=False
        ... )
    """

    def __init__(
        self,
        data_container,
        start: Optional[str] = None,
        stop: Optional[str] = None,
        days_to_forecast: Optional[int] = None,
        forecaster: str = "var",
        **forecaster_kwargs,
    ):
        """
        Initialize the SIRD Model.

        Args:
            data_container: DataContainer instance with preprocessed data
            start: Start date for model training (YYYY-MM-DD format)
            stop: Stop date for model training (YYYY-MM-DD format)
            days_to_forecast: Number of days to forecast ahead
            forecaster: Forecasting backend to use. Options:
                - 'var' (default): Vector Autoregression (statsmodels)
                - 'prophet': Facebook Prophet
                - 'arima': Auto-ARIMA (pmdarima)
                - 'lstm': LSTM neural network (stub - not yet implemented)
            **forecaster_kwargs: Backend-specific configuration parameters.
                For VAR: max_lag, ic (information criterion)
                For Prophet: yearly_seasonality, weekly_seasonality, changepoint_prior_scale
                For ARIMA: max_p, max_q, seasonal

        Examples:
            >>> # Default VAR backend (100% backward compatible)
            >>> model = Model(container, start="2020-03-01", stop="2020-12-31")
            >>>
            >>> # Prophet with custom seasonality
            >>> model = Model(
            ...     container,
            ...     forecaster="prophet",
            ...     yearly_seasonality=True,
            ...     changepoint_prior_scale=0.05
            ... )
            >>>
            >>> # ARIMA with custom parameters
            >>> model = Model(
            ...     container,
            ...     forecaster="arima",
            ...     max_p=3,
            ...     max_q=3,
            ...     seasonal=False
            ... )
        """
        # Data and model attributes
        self.data: Optional[pd.DataFrame] = None
        self.data_container = data_container
        self.window = data_container.window
        self.start = start
        self.stop = stop

        # Model parameters
        self.days_to_forecast = days_to_forecast

        # Forecasting configuration
        self.forecaster_name = forecaster
        self.forecaster_kwargs = forecaster_kwargs

        self.data = reindex_data(data_container.data, start, stop)

        # Select only logit ratios that exist in the data (SIRD vs SIRDV)
        available_logit_ratios = [r for r in LOGIT_RATIOS if r in self.data.columns]
        self.logit_ratios_values = self.data[available_logit_ratios].values
        self.active_logit_ratios = available_logit_ratios  # Store for later use

        # Detect vaccination presence
        self.has_vaccination = "logit_delta" in available_logit_ratios

        # Log model type detection
        n_rates = len(available_logit_ratios)
        model_type = "SIRDV" if n_rates == 4 else "SIRD"
        logging.info(
            f"Model initialized with {n_rates} rates ({model_type} mode), "
            f"forecaster='{forecaster}'"
        )

        # Forecasting component - use orchestrator for multi-backend support
        self.var_forecasting = ForecastingOrchestrator(
            self.data,
            self.logit_ratios_values,
            self.window,
            active_logit_ratios=available_logit_ratios,
            backend=forecaster,
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
        """
        Create the forecasting model for logit-transformed rates.

        This prepares the internal forecaster (VAR, Prophet, ARIMA, etc.) on the
        logit-transformed α, β, γ (and optionally δ for SIRDV) rates using the
        configured smoothing window.

        Args:
            **kwargs: Backend-specific creation parameters (forwarded to backend)

        Examples:
            >>> from epydemics import Model, process_data_from_owid
            >>> raw = process_data_from_owid("OWID_WRL")
            >>> container = DataContainer(raw, window=7)
            >>>
            >>> # Default VAR backend
            >>> model = Model(container, start="2020-03-01", stop="2020-12-31")
            >>> model.create_model()
            >>>
            >>> # Prophet backend
            >>> model = Model(container, forecaster="prophet")
            >>> model.create_model()
        """
        self.var_forecasting.create_logit_ratios_model(*args, **kwargs)

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
        """
        Fit the forecasting model to the data.

        Merges initialization-time kwargs (from __init__) with call-time kwargs,
        with call-time kwargs taking precedence. This allows flexible configuration:

        - Set defaults at initialization: Model(..., max_lag=10)
        - Override at fit time: model.fit_model(max_lag=15)

        Args:
            **kwargs: Backend-specific parameters. Common options:
                For VAR:
                    max_lag: Maximum lag order for selection (default from settings)
                    ic: Information criterion ('aic', 'bic', etc.)
                For Prophet:
                    yearly_seasonality: Enable yearly patterns
                    weekly_seasonality: Enable weekly patterns
                    changepoint_prior_scale: Trend flexibility
                For ARIMA:
                    max_p: Maximum AR order
                    max_q: Maximum MA order
                    seasonal: Enable seasonal ARIMA

        Examples:
            >>> # VAR with defaults
            >>> model = Model(container)
            >>> model.create_model()
            >>> model.fit_model(max_lag=10)
            >>>
            >>> # VAR with init-time and fit-time config
            >>> model = Model(container, max_lag=5)
            >>> model.fit_model(ic="bic")  # Uses max_lag=5, ic="bic"
            >>>
            >>> # Prophet with seasonality
            >>> model = Model(container, forecaster="prophet")
            >>> model.fit_model(yearly_seasonality=True)
        """
        settings = get_settings()

        # Merge init-time kwargs with call-time kwargs (call-time takes precedence)
        merged_kwargs = {**self.forecaster_kwargs, **kwargs}

        # Apply backend-specific defaults from settings
        if self.forecaster_name == "var":
            merged_kwargs.setdefault("max_lag", settings.VAR_MAX_LAG)
            merged_kwargs.setdefault("ic", settings.VAR_CRITERION)

        self.var_forecasting.fit_logit_ratios_model(*args, **merged_kwargs)
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
        """
        Generate forecasts for the specified number of steps.

        After fitting the model, this generates forecasts for the logit-transformed
        rates and initializes the simulation engine for downstream simulations.

        Args:
            steps: Number of forecast steps (days). If None, uses previously set value.

        Examples:
            >>> model.create_model()
            >>> model.fit_model()
            >>> model.forecast(steps=30)
        """
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
        """
        Generate results for all compartments.

        Aggregates simulation outputs into the final `results` structure
        (S, I, R, D, A, C) across confidence levels.

        Raises:
            RuntimeError: If simulation has not been executed yet

        Examples:
            >>> model.run_simulations()
            >>> model.generate_result()
            >>> assert model.results is not None
        """
        settings = get_settings()

        # Helper: compute a deterministic cache key from forecast + last history state
        def _hash_series_values(s: pd.Series) -> str:
            # Use raw bytes for stability
            h = hashlib.sha256()
            h.update(s.to_numpy().tobytes())
            h.update(str(s.dtype).encode("utf-8"))
            return h.hexdigest()

        def _compute_cache_key() -> str:
            last_hist = self.data.iloc[-1]

            # Build initial state with required compartments
            initial_state_keys = [
                "A",
                "C",
                "S",
                "I",
                "R",
                "D",
                "alpha",
                "beta",
                "gamma",
            ]
            if self.has_vaccination:
                initial_state_keys.extend(["V", "delta"])

            initial_state = {
                k: float(last_hist[k])
                for k in initial_state_keys
                if k in last_hist.index
            }

            # Build rates hash with required rates
            rates_to_hash = ["alpha", "beta", "gamma"]
            if self.has_vaccination:
                rates_to_hash.append("delta")

            rates_hash = {
                ratio: {
                    level: _hash_series_values(
                        self.forecasting_box[ratio][level].loc[
                            self.forecasting_interval
                        ]
                    )
                    for level in FORECASTING_LEVELS
                }
                for ratio in rates_to_hash
                if ratio in self.forecasting_box
            }

            payload: Dict[str, Any] = {
                "pkg_version": _get_pkg_version(),
                "start": self.start,
                "stop": self.stop,
                "window": self.window,
                "days_to_forecast": self.days_to_forecast,
                "has_vaccination": self.has_vaccination,
                "forecaster": self.forecaster_name,  # Include backend in cache key
                "forecaster_kwargs": self.forecaster_kwargs,  # Include config in cache key
                "interval": [d.strftime("%Y-%m-%d") for d in self.forecasting_interval],
                "initial_state": initial_state,
                "rates_hash": rates_hash,
            }
            blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
            return hashlib.sha256(blob).hexdigest()

        def _cache_dir_for_key(key: str) -> Path:
            base = Path(settings.CACHE_DIR)
            return base / key

        def _load_from_cache(dir_path: Path) -> Optional[Box]:
            meta_path = dir_path / "meta.json"
            if not meta_path.exists():
                return None
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                return None
            if (
                settings.CACHE_STRICT_VERSION
                and meta.get("pkg_version") != _get_pkg_version()
            ):
                return None

            box = Box()
            try:
                # Load all CSV files in the cache directory (dynamic compartments)
                for comp_file in dir_path.glob("*.csv"):
                    comp = comp_file.stem  # Get compartment name from filename
                    df = pd.read_csv(comp_file, index_col=0, parse_dates=True)
                    # Ensure index aligns to forecasting interval
                    df = df.loc[self.forecasting_interval]
                    box[comp] = df
                # Ensure we have at least the core SIRD compartments
                required_comps = ["C", "I", "R", "D"]
                if not all(comp in box for comp in required_comps):
                    return None
                return box
            except Exception:
                return None

        def _save_to_cache(dir_path: Path, results_box: Box) -> None:
            dir_path.mkdir(parents=True, exist_ok=True)
            meta = {
                "pkg_version": _get_pkg_version(),
                "start": str(self.start) if self.start else None,
                "stop": str(self.stop) if self.stop else None,
                "window": int(self.window) if self.window is not None else None,
                "days_to_forecast": int(self.days_to_forecast)
                if self.days_to_forecast is not None
                else None,
            }
            (dir_path / "meta.json").write_text(
                json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8"
            )
            # Only save compartments that exist in results
            for comp in results_box.keys():
                results_box[comp].to_csv(dir_path / f"{comp}.csv")

        # Attempt cache if enabled
        cache_used = False
        if settings.RESULT_CACHING_ENABLED:
            try:
                key = _compute_cache_key()
                cdir = _cache_dir_for_key(key)
                cached = _load_from_cache(cdir)
                if cached is not None:
                    logging.info("Loaded results from cache: %s", cdir)
                    self.results = cached
                    cache_used = True
                else:
                    logging.debug("No cache hit for key: %s", key)
            except Exception as e:
                logging.debug("Result cache check failed: %s", e)

        if not cache_used:
            if self.simulation_engine is None:
                raise RuntimeError(
                    "Forecast and simulation must be generated before generating results."
                )
            self.simulation_engine.generate_result()
            self.results = self.simulation_engine.results

            # Save to cache if enabled
            if settings.RESULT_CACHING_ENABLED:
                try:
                    key = _compute_cache_key()
                    cdir = _cache_dir_for_key(key)
                    _save_to_cache(cdir, self.results)
                    logging.info("Saved results to cache: %s", cdir)
                except Exception as e:
                    logging.error("Result cache save failed: %s", e, exc_info=True)

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
            >>> model.create_model()
            >>> model.fit_model()
            >>> model.forecast(steps=30)
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
                "Call forecast() first."
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

        Examples:
            >>> # Visualize confirmed cases with test split overlay
            >>> model.visualize_results("C", testing_data=testing_data, log_response=True)
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

        Examples:
            >>> testing = container.data.loc[model.forecasting_interval]
            >>> eval_dict = model.evaluate_forecast(testing)
            >>> # Save results to JSON
            >>> model.evaluate_forecast(testing, save_evaluation=True, filename="evaluation_output")
        """
        return _evaluate_forecast(
            results=self.results if self.results else self.simulation_engine.results,
            testing_data=testing_data,
            compartment_codes=compartment_codes,
            save_evaluation=save_evaluation,
            filename=filename,
        )
