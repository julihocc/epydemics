"""Test backward compatibility during refactoring."""

import pytest


def test_import_original_functionality():
    """Test that we can still import the original functionality."""
    # This should work throughout the refactoring
    from epydemics import DataContainer, Model, process_data_from_owid

    # Verify classes are importable
    assert DataContainer is not None
    assert Model is not None
    assert process_data_from_owid is not None


def test_import_constants():
    """Test that constants are importable."""
    from epydemics import ratios, compartments, compartment_labels

    # Verify basic constants
    assert isinstance(ratios, list)
    assert isinstance(compartments, list)
    assert isinstance(compartment_labels, dict)

    # Verify expected values
    assert "alpha" in ratios
    assert "C" in compartments
    assert "Confirmed" in compartment_labels.values()


def test_package_version():
    """Test that package version is accessible."""
    import epydemics

    assert hasattr(epydemics, "__version__")
    assert epydemics.__version__ == "0.6.0-dev"


def test_package_metadata():
    """Test that package metadata is accessible."""
    import epydemics

    assert hasattr(epydemics, "__author__")
    assert hasattr(epydemics, "__email__")
    assert epydemics.__author__ == "Juliho David Castillo Colmenares"
