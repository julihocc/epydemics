"""
Data preprocessing utilities.

This module handles the cleaning, smoothing, and temporal alignment of
epidemiological data before feature extraction.
"""

import logging
from typing import Optional

import pandas as pd


def preprocess_data(data: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Preprocess raw data by applying rolling window smoothing and reindexing.

    Args:
        data: Raw input DataFrame
        window: Rolling window size for smoothing

    Returns:
        Preprocessed DataFrame
    """
    # Apply rolling window smoothing
    smoothed_data = data.rolling(window=window).mean()[window:]

    # Reindex to ensure consistent date range
    reindexed_data = reindex_data(smoothed_data)

    return reindexed_data


def reindex_data(
    data: pd.DataFrame, start: Optional[str] = None, stop: Optional[str] = None
) -> pd.DataFrame:
    """
    Reindex DataFrame to a consistent daily date range and forward fill missing values.

    Args:
        data: DataFrame to reindex
        start: Start date (ISO format string), defaults to data minimum
        stop: Stop date (ISO format string), defaults to data maximum

    Returns:
        Reindexed DataFrame with daily frequency

    Raises:
        ValueError: If start > stop or dates are outside data range
    """
    # Handle case where data has no rows
    if len(data) == 0:
        return data

    # Convert dates and set defaults
    start_date = pd.to_datetime(start) if start is not None else data.index.min()
    stop_date = pd.to_datetime(stop) if stop is not None else data.index.max()

    # Validate date range
    if start_date > stop_date:
        raise ValueError("Start date is after stop date")

    if start_date < data.index[0]:
        raise ValueError("Start date is before first date on confirmed cases")

    if stop_date > data.index[-1]:
        raise ValueError("Stop date is after last date of updated cases")

    try:
        logging.debug(
            f"Reindex data from {start_date} to {stop_date} shape: {data.shape}"
        )
        reindex = pd.date_range(start=start_date, end=stop_date, freq="D")
        reindexed_data = data.reindex(reindex)
    except Exception as e:
        raise Exception(f"Could not reindex data: {e}")

    try:
        # Use forward fill for missing values
        reindexed_data = reindexed_data.ffill()
    except Exception as e:
        raise Exception(f"Could not fill missing values: {e}")

    return reindexed_data
