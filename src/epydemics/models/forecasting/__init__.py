"""
Forecasting models for epidemiological parameters.

This module provides interfaces and implementations for forecasting time-dependent
parameters (like infection rates) using various statistical and ML methods.
"""

from .base import BaseForecaster
from .orchestrator import ForecastingOrchestrator
from .registry import ForecasterRegistry, register_forecaster
from .var import VARForecaster

__all__ = [
    "BaseForecaster",
    "ForecastingOrchestrator",
    "ForecasterRegistry",
    "register_forecaster",
    "VARForecaster",
]
