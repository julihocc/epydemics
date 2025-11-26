"""
Forecasting models for epidemiological parameters.

This module provides interfaces and implementations for forecasting time-dependent
parameters (like infection rates) using various statistical and ML methods.
"""

from .var import VARForecaster

__all__ = ["VARForecaster"]
