"""
Configuration management for the epydemics library.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings for the epydemics library.

    Settings are loaded in the following order (with later sources
    overriding earlier ones):
    1. Default values defined in the class.
    2. Environment variables.
    3. .env file (if found).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Data Processing Settings ---
    WINDOW_SIZE: int = Field(7, description="Default window size for data processing.")
    RECOVERY_LAG: int = Field(14, description="Default recovery lag in days.")

    # --- OWID Data Settings ---
    OWID_DATA_URL: str = Field(
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-19-data.csv",
        description="URL for the OWID COVID-19 data.",
    )
    DEFAULT_ISO_CODES: List[str] = Field(
        ["USA", "GBR", "DEU", "FRA", "ITA"],
        description="Default ISO codes for data filtering.",
    )

    # --- Model Parameters ---
    VAR_MAX_LAG: Optional[int] = Field(
        None, description="Maximum lag for VAR model (None for auto-selection)."
    )
    VAR_CRITERION: str = Field(
        "aic", description="Criterion for VAR lag order selection (e.g., 'aic', 'bic')."
    )

    # --- Logging Settings ---
    LOG_LEVEL: str = Field("INFO", description="Default logging level.")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Default logging format.",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()

