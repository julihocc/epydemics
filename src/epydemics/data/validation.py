"""
Data validation utilities.

This module provides functions for validating epidemiological data structures
and types to ensure data integrity before processing.
"""

import pandas as pd
from ..core.exceptions import NotDataFrameError


def validate_data(training_data: pd.DataFrame) -> None:
    """
    Validate that the input data is a pandas DataFrame.

    Args:
        training_data: The data to validate

    Raises:
        NotDataFrameError: If the data is not a pandas DataFrame
    """
    if not isinstance(training_data, pd.DataFrame):
        raise NotDataFrameError("raw data must be a pandas DataFrame")
