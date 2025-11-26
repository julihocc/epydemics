"""Integration tests for backward compatibility."""


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
    from epydemics import COMPARTMENTS, RATIOS

    # Verify basic constants
    assert isinstance(RATIOS, list)
    assert isinstance(COMPARTMENTS, list)

    # Verify expected values
    assert "alpha" in RATIOS
    assert "C" in COMPARTMENTS


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
