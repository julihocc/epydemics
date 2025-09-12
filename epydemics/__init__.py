"""Epydemics: Advanced epidemiological modeling and forecasting.

This package provides tools for modeling and analyzing epidemic data using
discrete SIRD models combined with time series analysis.

Version: 0.6.0-dev (Phase 1 Refactoring)
"""

# Import specific constants and exceptions to avoid star imports
from .core.constants import (
    CENTRAL_TENDENCY_METHODS,
    COMPARTMENTS,
    FORECASTING_LEVELS,
    LOGIT_RATIOS,
    RATIOS,
)
from .core.exceptions import (
    DataValidationError,
    DateRangeError,
    EpydemicsError,
    NotDataFrameError,
)

# Import main functionality from modular structure
from .data.container import DataContainer, validate_data
from .epydemics import process_data_from_owid
from .models.sird import Model
from .utils.transformations import prepare_for_logit_function

__version__ = "0.6.0-dev"
__author__ = "Juliho David Castillo Colmenares"
__email__ = "juliho.colmenares@gmail.com"

# Define __all__ for explicit exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Constants
    "RATIOS",
    "LOGIT_RATIOS",
    "COMPARTMENTS",
    "FORECASTING_LEVELS",
    "CENTRAL_TENDENCY_METHODS",
    # Exceptions
    "EpydemicsError",
    "NotDataFrameError",
    "DataValidationError",
    "DateRangeError",
    # Main classes and functions
    "DataContainer",
    "Model",
    "process_data_from_owid",
    "validate_data",
    "prepare_for_logit_function",
]
