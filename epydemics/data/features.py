"""
Feature engineering utilities.

This module contains functions for calculating SIRD compartments, epidemiological rates,
and applying transformations (like logit) to prepare data for modeling.
"""

import logging
from typing import Union

import pandas as pd

from epydemics.core.config import get_settings

# Import constants from the core module
from ..core.constants import LOGIT_RATIOS, RATIOS


def prepare_for_logit_function(data: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare rate data for logit transformation by ensuring values are in (0,1).

    Args:
        data: DataFrame containing rate columns

    Returns:
        DataFrame with rates bounded between 0 and 1
    """
    data = data.copy()

    # Ensure rates are within (0,1) bounds for logit transformation
    for ratio in RATIOS:
        if ratio in data.columns:
            # Replace NaN and infinite values
            data[ratio] = data[ratio].replace(
                [float("inf"), -float("inf")], float("nan")
            )

            # Bound values between small epsilon and (1-epsilon)
            epsilon = 1e-10
            data[ratio] = data[ratio].clip(lower=epsilon, upper=1 - epsilon)

    return data


def logit_function(x: Union[float, pd.Series]) -> Union[float, pd.Series]:
    """
    Compute the logit transformation: log(x/(1-x)).

    Args:
        x: Value(s) to transform, must be in (0,1)

    Returns:
        Logit-transformed value(s)
    """
    import numpy as np

    return np.log(x / (1 - x))


def logistic_function(x: Union[float, pd.Series]) -> Union[float, pd.Series]:
    """
    Compute the logistic (inverse logit) transformation: 1/(1+exp(-x)).

    Args:
        x: Value(s) to transform

    Returns:
        Logistic-transformed value(s)
    """
    import numpy as np

    return 1 / (1 + np.exp(-x))


def add_logit_ratios(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add logit-transformed ratio columns to the DataFrame.

    Args:
        data: DataFrame containing rate columns

    Returns:
        DataFrame with additional logit rate columns
    """
    data = data.copy()

    # Add logit transformations for each ratio
    ratio_pairs = list(zip(RATIOS, LOGIT_RATIOS))
    for ratio, logit_ratio in ratio_pairs:
        if ratio in data.columns:
            try:
                data[logit_ratio] = logit_function(data[ratio])
            except Exception as e:
                logging.warning(f"Could not compute logit for {ratio}: {e}")
                data[logit_ratio] = float("nan")

    return data


def feature_engineering(data: pd.DataFrame) -> pd.DataFrame:
    """
    Perform feature engineering to create SIRD compartments and rate calculations.

    This function calculates:
    - SIRD compartments (S, I, R, D)
    - Difference values (dC, dI, dR, dD, etc.)
    - Epidemiological rates (alpha, beta, gamma)
    - R0 calculation
    - Logit transformations of rates

    Args:
        data: Preprocessed DataFrame with basic columns C, D, N

    Returns:
        DataFrame with full feature set for epidemiological modeling
    """
    logging.debug(f"When starting feature engineering, columns are {data.columns}")

    # Create a copy to avoid modifying original
    engineered_data = data.copy()

    # Calculate SIRD compartments
    # R: Recovered (using recovery_lag from settings)
    settings = get_settings()
    engineered_data = engineered_data.assign(
        R=engineered_data["C"]
        .shift(settings.RECOVERY_LAG)
        .fillna(0)
        - engineered_data["D"]
    )

    # I: Currently infected (active cases)
    engineered_data = engineered_data.assign(
        I=engineered_data["C"] - engineered_data["R"] - engineered_data["D"]
    )

    # S: Susceptible population
    engineered_data = engineered_data.assign(
        S=engineered_data["N"] - engineered_data["C"]
    )

    # A: At-risk population (S + I)
    engineered_data = engineered_data.assign(
        A=engineered_data["S"] + engineered_data["I"]
    )

    # Calculate differences (daily changes)
    engineered_data = engineered_data.assign(dC=-engineered_data["C"].diff(periods=-1))
    engineered_data = engineered_data.assign(dA=-engineered_data["A"].diff(periods=-1))
    engineered_data = engineered_data.assign(dS=-engineered_data["S"].diff(periods=-1))
    engineered_data = engineered_data.assign(dI=-engineered_data["I"].diff(periods=-1))
    engineered_data = engineered_data.assign(dR=-engineered_data["R"].diff(periods=-1))
    engineered_data = engineered_data.assign(dD=-engineered_data["D"].diff(periods=-1))

    # Calculate epidemiological rates
    # Alpha: infection rate
    engineered_data = engineered_data.assign(
        alpha=(engineered_data.A * engineered_data.dC)
        / (engineered_data.I * engineered_data.S)
    )

    # Beta: recovery rate
    engineered_data = engineered_data.assign(
        beta=engineered_data.dR / engineered_data.I
    )

    # Gamma: mortality rate
    engineered_data = engineered_data.assign(
        gamma=engineered_data.dD / engineered_data.I
    )

    # R0: Basic reproduction number
    engineered_data = engineered_data.assign(
        R0=engineered_data["alpha"]
        / (engineered_data["beta"] + engineered_data["gamma"])
    )

    logging.debug(f"When completing assignments, columns are {engineered_data.columns}")

    # Prepare rates for logit transformation and apply it
    engineered_data = prepare_for_logit_function(engineered_data)
    engineered_data = add_logit_ratios(engineered_data)

    # Final cleanup: forward fill then zero fill any remaining NaN values
    engineered_data = engineered_data.ffill().fillna(0)

    logging.debug(
        f"When completing feature engineering, columns are {engineered_data.columns}"
    )

    return engineered_data
