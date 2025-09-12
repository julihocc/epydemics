"""
Constants for the Epydemics package.

This module contains all the constant values used throughout the package,
including rate names, compartment identifiers, and analysis parameters.

The constants are organized by their usage domain and properly typed
for better code clarity and IDE support.
"""

from typing import List, Final

# Epidemic model rate names
# These are the three key rates in the SIRD model
RATIOS: Final[List[str]] = ["alpha", "beta", "gamma"]

# Logit-transformed rate names for VAR modeling
# Each corresponds to logit(rate) transformation for time series analysis
LOGIT_RATIOS: Final[List[str]] = ["logit_alpha", "logit_beta", "logit_gamma"]

# SIRD compartment identifiers
# A=Affected, C=Cases, S=Susceptible, I=Infected, R=Recovered, D=Deaths
COMPARTMENTS: Final[List[str]] = ["A", "C", "S", "I", "R", "D"]

# Forecasting confidence levels
# Used for uncertainty quantification in Monte Carlo simulations
FORECASTING_LEVELS: Final[List[str]] = ["lower", "point", "upper"]

# Central tendency calculation methods
# Statistical measures for summarizing simulation results
CENTRAL_TENDENCY_METHODS: Final[List[str]] = ["mean", "median", "gmean", "hmean"]

# Export all constants for easy importing
__all__ = [
    "RATIOS",
    "LOGIT_RATIOS",
    "COMPARTMENTS",
    "FORECASTING_LEVELS",
    "CENTRAL_TENDENCY_METHODS",
]
