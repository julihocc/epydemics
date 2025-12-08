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

    **New in v0.9.0**: Supports both cumulative and incidence mode for different
    data reporting patterns.

    Attributes:
        raw_data: Original input DataFrame
        window: Rolling window size for smoothing operations
        mode: Data interpretation mode ('cumulative' or 'incidence')
        data: Processed DataFrame with full feature engineering

    Examples:
        >>> # COVID-19 style: cumulative cases (default)
        >>> data = pd.DataFrame({'C': [100, 150, 200], 'D': [1, 2, 3], 'N': [1e6]*3})
        >>> container = DataContainer(data)  # mode='cumulative' by default

        >>> # Measles style: incident cases per year
        >>> data = pd.DataFrame({'I': [50, 30, 80], 'D': [1, 1, 2], 'N': [1e6]*3})
        >>> container = DataContainer(data, mode='incidence')
    """

    def __init__(
        self, raw_data: pd.DataFrame, window: int = None, mode: str = "cumulative"
    ) -> None:
        """
        Initialize DataContainer with raw epidemiological data.

        Args:
            raw_data: DataFrame with required columns depending on mode:
                     - cumulative mode: ['C', 'D', 'N'] where:
                       * C = cumulative confirmed cases (monotonically increasing)
                       * D = cumulative deaths (monotonically increasing)
                       * N = population (constant or slowly varying)
                     - incidence mode: ['I', 'D', 'N'] where:
                       * I = incident cases per period (can vary up/down)
                       * D = cumulative deaths (monotonically increasing)
                       * N = population (constant or slowly varying)
            window: Rolling window size for smoothing (default: 7 from config).
                   Larger values (e.g., 14) provide smoother rates.
                   Smaller values (e.g., 3) preserve more variation.
            mode: Data interpretation mode (default: 'cumulative')
                 - 'cumulative': Input C is cumulative, derives I = dC
                   Use for: COVID-19, flu, ongoing epidemics
                 - 'incidence': Input I is incident, derives C = cumsum(I)
                   Use for: Measles, polio, diseases with elimination cycles

        Raises:
            NotDataFrameError: If raw_data is not a pandas DataFrame
            DataValidationError: If required columns missing for specified mode
            ValueError: If mode not in ['cumulative', 'incidence']

        Examples:
            >>> # Daily COVID-19 data (cumulative)
            >>> container = DataContainer(covid_data, window=7, mode='cumulative')

            >>> # Annual measles data (incidence)
            >>> container = DataContainer(measles_data, window=3, mode='incidence')

            >>> # Access processed data
            >>> print(container.data.head())
            >>> print(f"Mode: {container.mode}")

        See Also:
            - examples/notebooks/07_incidence_mode_measles.ipynb
            - docs/USER_GUIDE.md: Incidence Mode section
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
