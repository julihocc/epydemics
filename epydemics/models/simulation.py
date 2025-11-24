"""
Epidemic simulation engine.
"""
import itertools
import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from box import Box
from scipy.stats import gmean, hmean

from ..core.constants import COMPARTMENTS, FORECASTING_LEVELS


class EpidemicSimulation:
    """
    Encapsulates the epidemic simulation logic extracted from the Model class.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        forecasting_box: Dict[str, pd.DataFrame],
        forecasting_interval: pd.DatetimeIndex,
    ):
        self.data = data
        self.forecasting_box = forecasting_box
        self.forecasting_interval = forecasting_interval

        self.simulation: Optional[Box] = None
        self.results: Optional[Box] = None

    def simulate_for_given_levels(
        self, simulation_levels: Tuple[str, str, str]
    ) -> pd.DataFrame:
        """
        Simulate epidemic dynamics for given rate confidence levels.

        Args:
            simulation_levels: Tuple of (alpha_level, beta_level, gamma_level)

        Returns:
            DataFrame with simulated compartment values
        """
        # Get initial state from the last historical data point
        last_hist = self.data.iloc[-1]

        # Current state variables
        S = last_hist.S
        I = last_hist.I
        R = last_hist.R
        D = last_hist.D
        # A and C are also needed (A used in alpha term)
        A = last_hist.A
        C = last_hist.C

        # Current rates (from history) used for the first step calculation
        alpha = last_hist.alpha
        beta = last_hist.beta
        gamma = last_hist.gamma

        # Get forecasted rates as numpy arrays for performance
        forecast_alphas = (
            self.forecasting_box["alpha"][simulation_levels[0]]
            .loc[self.forecasting_interval]
            .values
        )
        forecast_betas = (
            self.forecasting_box["beta"][simulation_levels[1]]
            .loc[self.forecasting_interval]
            .values
        )
        forecast_gammas = (
            self.forecasting_box["gamma"][simulation_levels[2]]
            .loc[self.forecasting_interval]
            .values
        )

        n_steps = len(self.forecasting_interval)

        # Pre-allocate result arrays
        # Columns: A, C, S, I, R, D, alpha, beta, gamma
        results = np.zeros((n_steps, 9))

        for i in range(n_steps):
            # Dynamics using CURRENT (previous step's) state and rates
            # S(t) = S(t-1) - I(t-1)*alpha(t-1)*S(t-1)/A(t-1)
            new_S = S - I * alpha * S / A

            # I(t) = I(t-1) + infection - recovery - death
            infection = I * alpha * S / A
            recovery = beta * I
            death = gamma * I

            new_I = I + infection - recovery - death
            new_R = R + recovery
            new_D = D + death

            new_C = new_I + new_R + new_D
            new_A = new_S + new_I

            # Get the rates for THIS forecasted step (to be used in NEXT iteration)
            new_alpha = forecast_alphas[i]
            new_beta = forecast_betas[i]
            new_gamma = forecast_gammas[i]

            # Store results
            results[i, 0] = new_A
            results[i, 1] = new_C
            results[i, 2] = new_S
            results[i, 3] = new_I
            results[i, 4] = new_R
            results[i, 5] = new_D
            results[i, 6] = new_alpha
            results[i, 7] = new_beta
            results[i, 8] = new_gamma

            # Update state for next iteration
            S, I, R, D, A, C = new_S, new_I, new_R, new_D, new_A, new_C
            alpha, beta, gamma = new_alpha, new_beta, new_gamma

        # Create DataFrame from results
        columns = ["A", "C", "S", "I", "R", "D", "alpha", "beta", "gamma"]
        simulation_df = pd.DataFrame(
            results, index=self.forecasting_interval, columns=columns
        )

        return simulation_df

    def create_simulation_box(self) -> None:
        """Create nested Box structure for storing simulation results."""
        self.simulation = Box()
        for logit_alpha_level in FORECASTING_LEVELS:
            self.simulation[logit_alpha_level] = Box()
            for logit_beta_level in FORECASTING_LEVELS:
                self.simulation[logit_alpha_level][logit_beta_level] = Box()
                for logit_gamma_level in FORECASTING_LEVELS:
                    self.simulation[logit_alpha_level][logit_beta_level][
                        logit_gamma_level
                    ] = None

    def run_simulations(self) -> None:
        """Run epidemic simulations for all combinations of rate confidence levels."""
        self.create_simulation_box()
        for current_levels in itertools.product(
            FORECASTING_LEVELS, FORECASTING_LEVELS, FORECASTING_LEVELS
        ):
            logit_alpha_level, logit_beta_level, logit_gamma_level = current_levels
            current_simulation = self.simulate_for_given_levels(current_levels)
            self.simulation[logit_alpha_level][logit_beta_level][
                logit_gamma_level
            ] = current_simulation

    def create_results_dataframe(self, compartment: str) -> pd.DataFrame:
        """
        Create results DataFrame for a specific compartment.

        Args:
            compartment: Compartment code (A, C, S, I, R, D)

        Returns:
            DataFrame with simulation results and central tendencies
        """
        results_dataframe = pd.DataFrame()
        logging.debug(results_dataframe.head())

        levels_interactions = itertools.product(
            FORECASTING_LEVELS, FORECASTING_LEVELS, FORECASTING_LEVELS
        )

        for (
            logit_alpha_level,
            logit_beta_level,
            logit_gamma_level,
        ) in levels_interactions:
            column_name = f"{logit_alpha_level}|{logit_beta_level}|{logit_gamma_level}"
            simulation = self.simulation[logit_alpha_level][logit_beta_level][
                logit_gamma_level
            ]
            results_dataframe[column_name] = simulation[compartment].values

        results_dataframe["mean"] = results_dataframe.mean(axis=1)
        results_dataframe["median"] = results_dataframe.median(axis=1)
        results_dataframe["gmean"] = results_dataframe.apply(gmean, axis=1)
        results_dataframe["hmean"] = results_dataframe.apply(hmean, axis=1)

        results_dataframe.index = self.forecasting_interval

        return results_dataframe

    def generate_result(self) -> None:
        """Generate results for all compartments."""
        self.results = Box()

        for compartment in COMPARTMENTS:
            self.results[compartment] = self.create_results_dataframe(compartment)
