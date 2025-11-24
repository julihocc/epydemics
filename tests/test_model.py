"""
Tests for Model class and SIRD modeling functionality.

Following TDD approach - these tests are written before implementation
to define expected behavior and ensure correct extraction.
"""

import itertools
import json
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

# Import from the original module during Phase 2 transition
from epydemics import Model
from epydemics.data import DataContainer


class TestModelInitialization:
    """Test Model class initialization and basic functionality."""

    @pytest.fixture
    def sample_data_container(self):
        """Create sample DataContainer for testing."""
        dates = pd.date_range("2020-01-01", periods=50, freq="D")
        sample_data = pd.DataFrame(
            {
                "C": np.cumsum(np.random.poisson(10, 50)) + 100,
                "D": np.cumsum(np.random.poisson(1, 50)) + 1,
                "N": [1000000] * 50,
            },
            index=dates,
        )
        return DataContainer(sample_data, window=7)

    def test_model_init_with_data_container(self, sample_data_container):
        """Test Model initialization with DataContainer."""
        # Act
        model = Model(sample_data_container)

        # Assert
        assert model.data_container is sample_data_container
        assert model.window == sample_data_container.window
        assert hasattr(model, "data")
        assert isinstance(model.data, pd.DataFrame)
        assert hasattr(model, "logit_ratios_values")

    def test_model_init_with_date_range(self, sample_data_container):
        """Test Model initialization with start/stop dates."""
        # Arrange
        start_date = "2020-01-10"
        stop_date = "2020-01-30"

        # Act
        model = Model(sample_data_container, start=start_date, stop=stop_date)

        # Assert
        assert model.start == start_date
        assert model.stop == stop_date
        assert len(model.data) <= len(sample_data_container.data)

    def test_model_init_with_forecast_days(self, sample_data_container):
        """Test Model initialization with custom forecast days."""
        # Arrange
        days_to_forecast = 14

        # Act
        model = Model(sample_data_container, days_to_forecast=days_to_forecast)

        # Assert
        assert model.days_to_forecast == days_to_forecast

    def test_model_init_sets_logit_ratios_values(self, sample_data_container):
        """Test that Model extracts logit ratios values correctly."""
        # Act
        model = Model(sample_data_container)

        # Assert
        assert hasattr(model, "logit_ratios_values")
        assert isinstance(model.logit_ratios_values, np.ndarray)
        assert model.logit_ratios_values.shape[1] == 3  # alpha, beta, gamma


class TestModelVARFunctionality:
    """Test VAR modeling functionality."""

    @pytest.fixture
    def fitted_model(self, sample_data_container):
        """Create a model with fitted VAR."""
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        return model

    def test_create_logit_ratios_model(self, sample_data_container):
        """Test VAR model creation."""
        # Arrange
        model = Model(sample_data_container)

        # Act
        model.create_model()

        # Assert
        assert model.logit_ratios_model is not None
        assert hasattr(model.logit_ratios_model, "fit")

    def test_fit_logit_ratios_model(self, sample_data_container):
        """Test VAR model fitting."""
        # Arrange
        model = Model(sample_data_container)
        model.create_model()

        # Act
        model.fit_model()

        # Assert
        assert model.logit_ratios_model_fitted is not None
        assert hasattr(model.logit_ratios_model_fitted, "forecast_interval")
        assert model.days_to_forecast is not None
        assert model.days_to_forecast > 0

    def test_forecast_logit_ratios(self, fitted_model):
        """Test logit ratios forecasting."""
        # Act
        fitted_model.forecast(steps=7)

        # Assert
        assert fitted_model.forecasting_box is not None
        assert fitted_model.forecasting_interval is not None
        assert len(fitted_model.forecasting_interval) == 7

        # Check that all rate forecasts exist
        for rate in [
            "alpha",
            "beta",
            "gamma",
            "logit_alpha",
            "logit_beta",
            "logit_gamma",
        ]:
            assert rate in fitted_model.forecasting_box

    def test_forecast_generates_confidence_intervals(self, fitted_model):
        """Test that forecasting generates proper confidence intervals."""
        # Act
        fitted_model.forecast(steps=5)

        # Assert
        forecasting_levels = ["lower", "point", "upper"]
        for rate in ["alpha", "beta", "gamma"]:
            rate_forecast = fitted_model.forecasting_box[rate]
            assert isinstance(rate_forecast, pd.DataFrame)
            assert len(rate_forecast) == 5
            for level in forecasting_levels:
                assert level in rate_forecast.columns

    def test_forecast_dates_alignment(self, fitted_model):
        """Test that forecast dates are properly aligned."""
        # Act
        fitted_model.forecast(steps=10)

        # Assert
        last_data_date = fitted_model.data.index[-1]
        expected_start = last_data_date + pd.Timedelta(days=1)

        assert fitted_model.forecast_index_start == expected_start
        assert fitted_model.forecasting_interval[0] == expected_start


class TestModelSimulation:
    """Test SIRD simulation functionality."""

    @pytest.fixture
    def model_with_forecasts(self, sample_data_container):
        """Create model with VAR forecasts ready for simulation."""
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        model.forecast(steps=5)
        return model




class TestModelResults:
    """Test results processing and aggregation."""

    @pytest.fixture
    def model_with_simulations(self, sample_data_container):
        """Create model with complete simulations."""
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        model.forecast(steps=5)
        model.run_simulations()
        return model



    def test_generate_result(self, model_with_simulations):
        """Test complete results generation."""
        # Act
        model_with_simulations.generate_result()

        # Assert
        results = model_with_simulations.results
        assert results is not None

        # Check all SIRD compartments have results
        compartments = ["A", "C", "S", "I", "R", "D"]
        for compartment in compartments:
            assert compartment in results
            assert isinstance(results[compartment], pd.DataFrame)


class TestModelVisualization:
    """Test visualization functionality."""

    @pytest.fixture
    def model_with_results(self, sample_data_container):
        """Create model with complete results."""
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        model.forecast(steps=5)
        model.run_simulations()
        model.generate_result()
        return model

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.plot")
    @patch("matplotlib.pyplot.title")
    @patch("matplotlib.pyplot.legend")
    @patch("matplotlib.pyplot.grid")
    def test_visualize_results_basic(
        self,
        mock_grid,
        mock_legend,
        mock_title,
        mock_plot,
        mock_show,
        model_with_results,
    ):
        """Test basic visualization functionality."""
        # Act
        model_with_results.visualize_results("C")

        # Assert
        assert mock_plot.called
        assert mock_title.called
        assert mock_legend.called
        assert mock_grid.called
        assert mock_show.called

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.plot")
    def test_visualize_results_with_testing_data(
        self, mock_plot, mock_show, model_with_results, sample_data_container
    ):
        """Test visualization with actual testing data overlay."""
        # Arrange
        testing_data = sample_data_container.data.tail(5)

        # Act
        model_with_results.visualize_results("C", testing_data=testing_data)

        # Assert
        assert mock_plot.called
        # Should have additional call for actual data
        call_count = mock_plot.call_count
        assert call_count > 4  # Gray lines + central tendencies + actual data


class TestModelEvaluation:
    """Test forecast evaluation functionality."""

    @pytest.fixture
    def model_with_results(self, sample_data_container):
        """Create model with results for evaluation."""
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        model.forecast(steps=5)
        model.run_simulations()
        model.generate_result()
        return model

    def test_evaluate_forecast_basic(self, model_with_results, sample_data_container):
        """Test basic forecast evaluation."""
        # Arrange
        testing_data = sample_data_container.data.tail(5)

        # Act
        evaluation = model_with_results.evaluate_forecast(testing_data)

        # Assert
        assert isinstance(evaluation, dict)

        # Default compartments to evaluate
        default_compartments = ["C", "D", "I"]
        for compartment in default_compartments:
            assert compartment in evaluation

        # Check metrics for each compartment
        central_methods = ["mean", "median", "gmean", "hmean"]
        expected_metrics = ["mae", "mse", "rmse", "mape", "smape"]

        for compartment in default_compartments:
            for method in central_methods:
                assert method in evaluation[compartment]
                for metric in expected_metrics:
                    assert metric in evaluation[compartment][method]
                    assert isinstance(
                        evaluation[compartment][method][metric], (int, float)
                    )

    def test_evaluate_forecast_custom_compartments(
        self, model_with_results, sample_data_container
    ):
        """Test evaluation with custom compartment selection."""
        # Arrange
        testing_data = sample_data_container.data.tail(5)
        custom_compartments = ["S", "R"]

        # Act
        evaluation = model_with_results.evaluate_forecast(
            testing_data, compartment_codes=custom_compartments
        )

        # Assert
        assert len(evaluation) == 2
        for compartment in custom_compartments:
            assert compartment in evaluation

    @patch("builtins.open", create=True)
    @patch("json.dump")
    def test_evaluate_forecast_save_results(
        self, mock_json_dump, mock_open, model_with_results, sample_data_container
    ):
        """Test saving evaluation results to JSON."""
        # Arrange
        testing_data = sample_data_container.data.tail(5)
        filename = "test_evaluation"

        # Act
        evaluation = model_with_results.evaluate_forecast(
            testing_data, save_evaluation=True, filename=filename
        )

        # Assert
        assert mock_open.called
        assert mock_json_dump.called
        # Should open file with correct name
        mock_open.assert_called_with(f"{filename}.json", "w")


class TestModelIntegration:
    """Integration tests for complete Model workflow."""

    def test_complete_workflow(self, sample_data_container):
        """Test complete end-to-end Model workflow."""
        # Arrange & Act - Complete pipeline
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        model.forecast(steps=7)
        model.run_simulations()
        model.generate_result()

        # Assert - All components should be populated
        assert model.logit_ratios_model_fitted is not None
        assert model.forecasting_box is not None
        assert model.simulation_engine.simulation is not None
        assert model.results is not None

        # Results should contain all compartments
        compartments = ["A", "C", "S", "I", "R", "D"]
        for compartment in compartments:
            assert compartment in model.results

    def test_model_performance_reasonable_time(self, sample_data_container):
        """Test that complete model workflow completes in reasonable time."""
        # Arrange
        import time

        # Act - Time the complete workflow
        start_time = time.time()
        model = Model(sample_data_container)
        model.create_model()
        model.fit_model()
        model.forecast(steps=5)  # Smaller forecast for speed
        model.run_simulations()
        model.generate_result()
        end_time = time.time()

        # Assert - Should complete within reasonable time (30 seconds max)
        execution_time = end_time - start_time
        assert (
            execution_time < 30.0
        ), f"Model workflow took {execution_time:.2f}s, expected <30s"

    def test_model_backward_compatibility(self, sample_data_container):
        """Test that Model maintains backward compatibility with existing usage."""
        # Act - Use Model the same way as legacy code
        model = Model(
            sample_data_container,
            start="2020-03-10",
            stop="2020-03-25",
            days_to_forecast=7,
        )

        # Assert - Should maintain same interface and attributes
        assert hasattr(model, "data_container")
        assert hasattr(model, "data")
        assert hasattr(model, "window")
        assert hasattr(model, "start")
        assert hasattr(model, "stop")
        assert hasattr(model, "days_to_forecast")

        # Should be able to create and fit model
        model.create_model()
        model.fit_model()
        assert model.logit_ratios_model is not None
        assert model.logit_ratios_model_fitted is not None
