





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













    def __init__(self, raw_data: pd.DataFrame, window: int = None) -> None:






        """






        Initialize DataContainer with raw epidemiological data.













        Args:






            raw_data: DataFrame with columns ['C', 'D', 'N'] representing






                     cumulative cases, deaths, and population






            window: Rolling window size for smoothing (default: 7 days, from config)













        Raises:






            NotDataFrameError: If raw_data is not a pandas DataFrame






        """






        settings = get_settings()






        self.raw_data = raw_data






        self.window = window if window is not None else settings.WINDOW_SIZE






        self.data = None





        # Validate input data


        validate_data(self.raw_data)





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





        # Apply feature engineering


        self.data = feature_engineering(self.data)


        logging.debug(f"Feature engineered data columns: {self.data.columns}")


        logging.debug(f"Data shape: {self.data.shape}")

