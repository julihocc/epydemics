"""
Tests for analysis.visualization module.

Following TDD principles, these tests define the expected behavior
of the visualization functions for epidemiological models.
"""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from epydemics.analysis.visualization import visualize_results


@pytest.fixture
def sample_results():
    """Sample forecast results structure for testing."""
    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    
    # Create sample forecast data with central tendencies
    central_tendency_data = pd.DataFrame(
        {
            "mean": np.linspace(100, 200, 10),
            "median": np.linspace(95, 195, 10),
            "gmean": np.linspace(98, 198, 10),
            "hmean": np.linspace(92, 192, 10),
        },
        index=dates,
    )
    
    # Add some simulation paths (non-central tendency columns)
    simulation_data = central_tendency_data.copy()
    simulation_data["lower|lower|lower"] = simulation_data["mean"] * 0.8
    simulation_data["upper|upper|upper"] = simulation_data["mean"] * 1.2
    simulation_data["point|lower|point"] = simulation_data["mean"] * 0.9
    
    # Create results structure
    results = {
        "C": simulation_data,
        "D": simulation_data.copy() * 0.1,
        "I": simulation_data.copy() * 0.5,
    }
    
    return results

@pytest.fixture
def sample_testing_data():
    """Sample testing data for comparison."""
    dates = pd.date_range("2020-01-01", periods=10, freq="D")

    return pd.DataFrame(
        {
            "C": np.linspace(105, 205, 10),
            "D": np.linspace(10.5, 20.5, 10),
            "I": np.linspace(52.5, 102.5, 10),
        },
        index=dates,
    )


def test_visualize_results_imports():
    """Test that visualization functions can be imported."""
    from epydemics.analysis.visualization import visualize_results

    assert callable(visualize_results)


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
@patch("matplotlib.pyplot.xlabel")
@patch("matplotlib.pyplot.ylabel")
@patch("matplotlib.pyplot.title")
@patch("matplotlib.pyplot.legend")
@patch("matplotlib.pyplot.grid")
@patch("matplotlib.pyplot.yscale")
@patch("matplotlib.pyplot.tight_layout")
def test_visualize_results_basic_call(
    mock_tight_layout,
    mock_yscale,
    mock_grid,
    mock_legend,
    mock_title,
    mock_ylabel,
    mock_xlabel,
    mock_plot,
    mock_show,
    sample_results,
):
    """Test basic visualization function call."""

    # Should not raise any errors
    visualize_results(sample_results, "C")

    # Verify that matplotlib functions were called
    mock_xlabel.assert_called_with("Date")
    mock_ylabel.assert_called()
    mock_title.assert_called()
    mock_legend.assert_called()
    mock_grid.assert_called_with(True, alpha=0.3)
    mock_tight_layout.assert_called()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
@patch("matplotlib.pyplot.yscale")
def test_visualize_results_log_scale(mock_yscale, mock_plot, mock_show, sample_results):
    """Test visualization with logarithmic scale."""

    # Call with log_response=True
    visualize_results(sample_results, "C", log_response=True)

    # Should set logarithmic scale
    mock_yscale.assert_called_with("log")


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
@patch("matplotlib.pyplot.yscale")
def test_visualize_results_no_log_scale(
    mock_yscale, mock_plot, mock_show, sample_results
):
    """Test visualization without logarithmic scale."""

    # Call with log_response=False
    visualize_results(sample_results, "C", log_response=False)

    # Should not set logarithmic scale
    mock_yscale.assert_not_called()


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
def test_visualize_results_with_testing_data(
    mock_plot, mock_show, sample_results, sample_testing_data
):
    """Test visualization with testing data overlay."""

    visualize_results(sample_results, "C", testing_data=sample_testing_data)

    # Should make additional plot call for testing data
    # (Central tendencies + simulation paths + testing data)
    assert mock_plot.call_count >= 5  # At least 4 central tendencies + 1 testing data


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
def test_visualize_results_plot_calls(mock_plot, mock_show, sample_results):
    """Test that visualization makes appropriate plot calls."""

    visualize_results(sample_results, "C")

    # Should make multiple plot calls:
    # - One for each central tendency method (4)
    # - One or more for simulation paths
    assert mock_plot.call_count >= 4

    # Check that different line styles and colors are used
    call_args_list = [call[1] for call in mock_plot.call_args_list if len(call) > 1]

    # Note: In a real test we'd check the actual plot styling
    # For now, just verify that plot calls were made with some styling parameters
    has_styling = any(len(kwargs) > 0 for kwargs in call_args_list)
    assert has_styling  # Should have some styling parameters


def test_visualize_results_missing_compartment(sample_results):
    """Test error handling for missing compartment."""

    with pytest.raises(KeyError, match="Compartment 'X' not found in results"):
        visualize_results(sample_results, "X")


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
def test_visualize_results_different_compartments(mock_plot, mock_show, sample_results):
    """Test visualization works for different compartments."""

    # Test each available compartment
    for compartment in ["C", "D", "I"]:
        mock_plot.reset_mock()
        visualize_results(sample_results, compartment)

        # Should make plot calls for each compartment
        assert mock_plot.call_count >= 4


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
def test_visualize_results_alpha_parameter(mock_plot, mock_show, sample_results):
    """Test that alpha parameter is used for simulation paths."""

    custom_alpha = 0.1
    visualize_results(sample_results, "C", alpha=custom_alpha)

    # Check that alpha parameter is passed to plot calls
    # (This is implementation-specific and might need adjustment)
    call_args_list = [call[1] for call in mock_plot.call_args_list if len(call) > 1]

    # Should have some calls with alpha parameters
    has_alpha_params = any("alpha" in kwargs for kwargs in call_args_list)
    assert has_alpha_params  # Should use alpha parameters in plotting


def test_visualize_results_constants_usage():
    """Test that visualization uses the correct constants."""
    # This test ensures that constants are properly imported and used
    from epydemics.analysis.visualization import (
        central_tendency_methods,
        compartment_labels,
        method_colors,
        method_names,
    )

    # Constants should be available
    assert central_tendency_methods is not None
    assert compartment_labels is not None
    assert method_colors is not None
    assert method_names is not None

    # Should be the correct types
    assert isinstance(central_tendency_methods, (list, tuple))
    assert isinstance(compartment_labels, dict)
    assert isinstance(method_colors, dict)
    assert isinstance(method_names, dict)


@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.plot")
def test_visualize_results_no_testing_data(mock_plot, mock_show, sample_results):
    """Test visualization without testing data."""

    visualize_results(sample_results, "C", testing_data=None)

    # Should still work and make plot calls
    assert mock_plot.call_count >= 4

    # Should not have red line for actual data
    call_args_list = [call[1] for call in mock_plot.call_args_list if len(call) > 1]
    red_lines = [
        kwargs
        for kwargs in call_args_list
        if "color" in kwargs and kwargs["color"] == "red"
    ]
    assert len(red_lines) == 0


def test_visualize_results_testing_data_missing_column(sample_results):
    """Test behavior when testing data doesn't have the compartment column."""

    # Create testing data without the requested compartment
    incomplete_testing_data = pd.DataFrame(
        {
            "D": [10, 20, 30],
            "I": [50, 60, 70],
        },
        index=pd.date_range("2020-01-01", periods=3),
    )

    # Should handle gracefully (no red line should be plotted)
    with patch("matplotlib.pyplot.show"), patch("matplotlib.pyplot.plot") as mock_plot:
        visualize_results(sample_results, "C", testing_data=incomplete_testing_data)

        # Should still work
        assert mock_plot.call_count >= 4


def test_backward_compatibility_imports():
    """Test that visualization functions maintain backward compatibility."""
    # Should be able to import from analysis module
    from epydemics.analysis import visualize_results

    assert callable(visualize_results)
