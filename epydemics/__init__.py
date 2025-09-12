"""
Epydemics: Advanced epidemiological modeling and forecasting.

This package provides tools for modeling and analyzing epidemic data using
discrete SIRD models combined with time series analysis.

Version: 0.6.0-dev (Phase 1 Refactoring)
"""

# Maintain backward compatibility - import everything from original module
# This will be updated as we refactor components

try:
    # Try to import from new modular structure
    from .core.constants import *
    from .core.exceptions import *
except ImportError:
    # Fall back to original module during transition
    pass

# Import from original module for now (will be gradually replaced)
from .epydemics import *

__version__ = "0.6.0-dev"
__author__ = "Juliho David Castillo Colmenares"
__email__ = "juliho.colmenares@gmail.com"
