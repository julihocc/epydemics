"""
Tests for constants module.

Following TDD principles, these tests define the expected behavior
of the constants module before implementation.
"""


def test_constants_module_imports():
    """Test that all constants can be imported from core.constants."""
    from epydemics.core.constants import (
        CENTRAL_TENDENCY_METHODS,
        COMPARTMENTS,
        FORECASTING_LEVELS,
        LOGIT_RATIOS,
        RATIOS,
    )

    # Basic import verification
    assert RATIOS is not None
    assert LOGIT_RATIOS is not None
    assert COMPARTMENTS is not None
    assert FORECASTING_LEVELS is not None
    assert CENTRAL_TENDENCY_METHODS is not None


def test_ratios_constants():
    """Test RATIOS constant has correct values and type."""
    from epydemics.core.constants import RATIOS

    expected = ["alpha", "beta", "gamma"]
    assert isinstance(RATIOS, list)
    assert RATIOS == expected
    assert len(RATIOS) == 3
    assert all(isinstance(item, str) for item in RATIOS)


def test_logit_ratios_constants():
    """Test LOGIT_RATIOS constant has correct values and type."""
    from epydemics.core.constants import LOGIT_RATIOS

    expected = ["logit_alpha", "logit_beta", "logit_gamma"]
    assert isinstance(LOGIT_RATIOS, list)
    assert LOGIT_RATIOS == expected
    assert len(LOGIT_RATIOS) == 3
    assert all(isinstance(item, str) for item in LOGIT_RATIOS)


def test_compartments_constants():
    """Test COMPARTMENTS constant has correct values and type."""
    from epydemics.core.constants import COMPARTMENTS

    expected = ["A", "C", "S", "I", "R", "D"]
    assert isinstance(COMPARTMENTS, list)
    assert COMPARTMENTS == expected
    assert len(COMPARTMENTS) == 6
    assert all(isinstance(item, str) for item in COMPARTMENTS)


def test_forecasting_levels_constants():
    """Test FORECASTING_LEVELS constant has correct values and type."""
    from epydemics.core.constants import FORECASTING_LEVELS

    expected = ["lower", "point", "upper"]
    assert isinstance(FORECASTING_LEVELS, list)
    assert FORECASTING_LEVELS == expected
    assert len(FORECASTING_LEVELS) == 3
    assert all(isinstance(item, str) for item in FORECASTING_LEVELS)


def test_central_tendency_methods_constants():
    """Test CENTRAL_TENDENCY_METHODS constant has correct values and type."""
    from epydemics.core.constants import CENTRAL_TENDENCY_METHODS

    expected = ["mean", "median", "gmean", "hmean"]
    assert isinstance(CENTRAL_TENDENCY_METHODS, list)
    assert CENTRAL_TENDENCY_METHODS == expected
    assert len(CENTRAL_TENDENCY_METHODS) == 4
    assert all(isinstance(item, str) for item in CENTRAL_TENDENCY_METHODS)


def test_constants_immutability():
    """Test that constants are properly typed and documented."""
    from epydemics.core.constants import (
        CENTRAL_TENDENCY_METHODS,
        COMPARTMENTS,
        FORECASTING_LEVELS,
        LOGIT_RATIOS,
        RATIOS,
    )

    # Test that all constants are lists of strings
    for const in [
        RATIOS,
        LOGIT_RATIOS,
        COMPARTMENTS,
        FORECASTING_LEVELS,
        CENTRAL_TENDENCY_METHODS,
    ]:
        assert isinstance(const, list)
        assert all(isinstance(item, str) for item in const)
        assert len(const) > 0


def test_ratios_correspondence():
    """Test that RATIOS and LOGIT_RATIOS correspond correctly."""
    from epydemics.core.constants import LOGIT_RATIOS, RATIOS

    # Each logit ratio should correspond to a ratio
    for i, ratio in enumerate(RATIOS):
        expected_logit = f"logit_{ratio}"
        assert LOGIT_RATIOS[i] == expected_logit


def test_backward_compatibility():
    """Test that constants maintain backward compatibility with original module."""
    # Import from original location (should still work)
    import epydemics

    # These should exist in the original module
    assert hasattr(epydemics, "RATIOS")
    assert hasattr(epydemics, "LOGIT_RATIOS")
    assert hasattr(epydemics, "COMPARTMENTS")
    assert hasattr(epydemics, "FORECASTING_LEVELS")
    assert hasattr(epydemics, "CENTRAL_TENDENCY_METHODS")

    # Values should match
    from epydemics.core.constants import (
        CENTRAL_TENDENCY_METHODS,
        COMPARTMENTS,
        FORECASTING_LEVELS,
        LOGIT_RATIOS,
        RATIOS,
    )

    assert epydemics.RATIOS == RATIOS
    assert epydemics.LOGIT_RATIOS == LOGIT_RATIOS
    assert epydemics.COMPARTMENTS == COMPARTMENTS
    assert epydemics.FORECASTING_LEVELS == FORECASTING_LEVELS
    assert epydemics.CENTRAL_TENDENCY_METHODS == CENTRAL_TENDENCY_METHODS
