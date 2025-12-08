import logging

import pandas as pd

from epydemics.core.config import get_settings

from .validation import validate_data

from .preprocessing import preprocess_data

from .features import feature_engineering


class DataContainer:
    """

    Container for epidemiological data with preprocessing and feature engineering.

    The DataContainer class handles the transformation of raw epidemiological data

    into a format suitable for SIRD (Susceptible-Infected-Recovered-Deaths) modeling.

    It performs data validation, preprocessing with rolling window smoothing,

    and comprehensive feature engineering to create all necessary epidemiological

    variables and rates.

    Attributes:

        raw_data: Original input DataFrame

        window: Rolling window size for smoothing operations

        data: Processed DataFrame with full feature engineering

    """

    def __init__(
        self, raw_data: pd.DataFrame, window: int = None, mode: str = "cumulative"
    ) -> None:
        """

        Initialize DataContainer with raw epidemiological data.

        Args:

            raw_data: DataFrame with required columns depending on mode:

                     - cumulative mode: ['C', 'D', 'N'] (cumulative cases, deaths, population)

                     - incidence mode: ['I', 'D', 'N'] (incident cases, deaths, population)

            window: Rolling window size for smoothing (default: 7 days, from config)

            mode: Data mode - 'cumulative' (default) or 'incidence'.

                  cumulative: C(t) monotonically increasing (COVID-19 style)

                  incidence: I(t) can vary up/down (measles style)

        Raises:

            NotDataFrameError: If raw_data is not a pandas DataFrame

        """

        settings = get_settings()

        # Validate mode parameter

        if mode not in ["cumulative", "incidence"]:
            raise ValueError(
                f"Invalid mode '{mode}'. Must be 'cumulative' or 'incidence'"
            )

        self.raw_data = raw_data

        self.window = window if window is not None else settings.WINDOW_SIZE

        self.mode = mode

        self.data = None

        # Validate input data (mode-specific)

        validate_data(self.raw_data, mode=self.mode)

        # Run the processing pipeline

        self.process()

    def process(self) -> None:
        """

        Process the raw data through the preprocessing and feature engineering pipeline.

        This method:

        1. Applies preprocessing (smoothing, reindexing)

        2. Applies feature engineering (SIRD compartments, rates, logit transforms)

        3. Updates the self.data attribute with the result

        """

        # Process data through the pipeline

        self.data = preprocess_data(self.raw_data, window=self.window)

        logging.debug(f"Preprocessed data columns: {self.data.columns}")

        # Apply feature engineering (mode-aware)

        self.data = feature_engineering(self.data, mode=self.mode)

        logging.debug(f"Feature engineered data columns: {self.data.columns}")

        logging.debug(f"Data shape: {self.data.shape}")
