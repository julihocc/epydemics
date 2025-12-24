"""
Reporting tools for generating publication-ready analysis and visualizations.

This module provides high-level functions to create comprehensive reports,
summary statistics, and publication-quality figures from model results.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ..core.constants import COMPARTMENT_LABELS
from .evaluation import evaluate_forecast
from .formatting import format_time_axis
from .visualization import visualize_results


class ModelReport:
    """
    Generate comprehensive reports from epydemics model results.

    This class provides methods to create publication-ready reports including:
    - Summary statistics
    - Forecast visualizations
    - Evaluation metrics
    - Markdown/LaTeX export

    Examples:
        >>> report = ModelReport(model.results, testing_data)
        >>> report.generate_summary()
        >>> report.plot_forecast_panel()
        >>> report.export_markdown("results.md")
    """

    def __init__(
        self,
        results: Dict[str, Any],
        testing_data: Optional[pd.DataFrame] = None,
        compartments: Optional[List[str]] = None,
        model_name: str = "SIRD Model"
    ):
        """
        Initialize model report.

        Args:
            results: Model results dictionary from model.results
            testing_data: Optional test data for evaluation
            compartments: List of compartments to include (default: all)
            model_name: Name of the model for report headers
        """
        self.results = results
        self.testing_data = testing_data
        self.model_name = model_name

        # Auto-detect compartments if not provided
        if compartments is None:
            self.compartments = list(results.keys())
        else:
            self.compartments = compartments

        # Evaluation metrics (computed on demand)
        self._evaluation: Optional[Dict] = None

    def generate_summary(self) -> pd.DataFrame:
        """
        Generate summary statistics for all compartments.

        Returns:
            DataFrame with summary statistics (mean, median, std, min, max, etc.)
        """
        summary_data = []

        for comp in self.compartments:
            comp_data = self.results[comp]

            # Get mean and median if available
            if 'mean' in comp_data.columns:
                mean_val = comp_data['mean'].mean()
                median_val = comp_data['median'].mean() if 'median' in comp_data.columns else mean_val
                std_val = comp_data['mean'].std()
                min_val = comp_data['mean'].min()
                max_val = comp_data['mean'].max()

                summary_data.append({
                    'Compartment': COMPARTMENT_LABELS.get(comp, comp),
                    'Code': comp,
                    'Mean': mean_val,
                    'Median': median_val,
                    'Std Dev': std_val,
                    'Min': min_val,
                    'Max': max_val,
                    'Range': max_val - min_val,
                    'CV (%)': (std_val / mean_val * 100) if mean_val > 0 else 0
                })

        return pd.DataFrame(summary_data)

    def evaluate(self, compartments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluate forecast accuracy against test data.

        Args:
            compartments: List of compartments to evaluate (default: all)

        Returns:
            Dictionary with evaluation metrics

        Raises:
            ValueError: If no testing data provided
        """
        if self.testing_data is None:
            raise ValueError("Testing data required for evaluation")

        if self._evaluation is None:
            comp_tuple = tuple(compartments) if compartments else tuple(self.compartments)
            self._evaluation = evaluate_forecast(
                self.results,
                self.testing_data,
                compartment_codes=comp_tuple
            )

        return self._evaluation

    def get_evaluation_summary(self) -> pd.DataFrame:
        """
        Get evaluation metrics as a formatted DataFrame.

        Returns:
            DataFrame with evaluation metrics for each compartment
        """
        if self.testing_data is None:
            return pd.DataFrame({'Note': ['No testing data provided']})

        eval_metrics = self.evaluate()

        rows = []
        for comp, methods in eval_metrics.items():
            for method, metrics in methods.items():
                rows.append({
                    'Compartment': COMPARTMENT_LABELS.get(comp, comp),
                    'Method': method.title(),
                    'MAE': metrics['mae'],
                    'RMSE': metrics['rmse'],
                    'MAPE (%)': metrics['mape'],
                    'SMAPE (%)': metrics['smape']
                })

        return pd.DataFrame(rows)

    def plot_forecast_panel(
        self,
        figsize: Tuple[int, int] = (15, 10),
        save_path: Optional[Union[str, Path]] = None,
        dpi: int = 300
    ) -> Figure:
        """
        Create a multi-panel figure with forecasts for all compartments.

        Args:
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save figure
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure object
        """
        n_compartments = len(self.compartments)
        n_cols = 2
        n_rows = (n_compartments + 1) // 2

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_compartments > 1 else [axes]

        for idx, comp in enumerate(self.compartments):
            plt.sca(axes[idx])
            visualize_results(
                self.results,
                comp,
                testing_data=self.testing_data,
                log_response=False,
                format_axis=True
            )
            axes[idx].set_title(
                f"{COMPARTMENT_LABELS.get(comp, comp)} Forecast",
                fontsize=12,
                fontweight='bold'
            )

        # Hide unused subplots
        for idx in range(n_compartments, len(axes)):
            axes[idx].set_visible(False)

        fig.suptitle(f"{self.model_name} - Forecast Results", fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
            print(f"Figure saved to {save_path}")

        return fig

    def export_markdown(
        self,
        filepath: Union[str, Path],
        include_summary: bool = True,
        include_evaluation: bool = True,
        include_figure: bool = True
    ) -> None:
        """
        Export report as a Markdown file.

        Args:
            filepath: Path to save Markdown file
            include_summary: Include summary statistics
            include_evaluation: Include evaluation metrics (requires testing data)
            include_figure: Save and reference forecast figure
        """
        filepath = Path(filepath)
        lines = []

        # Header
        lines.append(f"# {self.model_name} - Forecast Report\n")
        lines.append(f"**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # Summary statistics
        if include_summary:
            lines.append("## Summary Statistics\n")
            summary_df = self.generate_summary()
            lines.append(summary_df.to_markdown(index=False))
            lines.append("\n")

        # Evaluation metrics
        if include_evaluation and self.testing_data is not None:
            lines.append("## Forecast Evaluation\n")
            eval_df = self.get_evaluation_summary()
            lines.append(eval_df.to_markdown(index=False))
            lines.append("\n")

        # Figure
        if include_figure:
            fig_path = filepath.parent / f"{filepath.stem}_forecast.png"
            self.plot_forecast_panel(save_path=fig_path)
            lines.append("## Forecast Visualization\n")
            lines.append(f"![Forecast Results]({fig_path.name})\n")

        # Write to file
        filepath.write_text('\n'.join(lines))
        print(f"Report exported to {filepath}")

    def export_latex_table(
        self,
        filepath: Union[str, Path],
        table_type: str = "summary"
    ) -> None:
        """
        Export results as a LaTeX table for publications.

        Args:
            filepath: Path to save LaTeX file
            table_type: Type of table ('summary' or 'evaluation')
        """
        filepath = Path(filepath)

        if table_type == "summary":
            df = self.generate_summary()
            caption = "Summary statistics for forecast results"
        elif table_type == "evaluation":
            if self.testing_data is None:
                raise ValueError("Testing data required for evaluation table")
            df = self.get_evaluation_summary()
            caption = "Forecast evaluation metrics"
        else:
            raise ValueError(f"Unknown table type: {table_type}")

        latex_str = df.to_latex(
            index=False,
            float_format="%.2f",
            caption=caption,
            label=f"tab:{table_type}"
        )

        filepath.write_text(latex_str)
        print(f"LaTeX table exported to {filepath}")


def create_comparison_report(
    models: Dict[str, Dict[str, Any]],
    testing_data: Optional[pd.DataFrame] = None,
    compartment: str = "C",
    save_path: Optional[Union[str, Path]] = None
) -> Figure:
    """
    Create a comparison report for multiple models.

    Args:
        models: Dictionary mapping model names to results dictionaries
        testing_data: Optional test data for all models
        compartment: Compartment to compare
        save_path: Optional path to save figure

    Returns:
        Matplotlib Figure object

    Examples:
        >>> models = {
        ...     "Baseline": baseline_model.results,
        ...     "With Intervention": intervention_model.results
        ... }
        >>> fig = create_comparison_report(models, test_data, "C")
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    for name, results in models.items():
        comp_data = results[compartment]
        if 'mean' in comp_data.columns:
            ax.plot(
                comp_data.index,
                comp_data['mean'],
                label=name,
                linewidth=2
            )

    # Plot actual data if provided
    if testing_data is not None and compartment in testing_data.columns:
        ax.plot(
            testing_data.index,
            testing_data[compartment],
            'k--',
            label='Actual',
            linewidth=2
        )

    ax.set_xlabel('Date')
    ax.set_ylabel(f"{COMPARTMENT_LABELS.get(compartment, compartment)}")
    ax.set_title(f"Model Comparison - {COMPARTMENT_LABELS.get(compartment, compartment)}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format time axis
    format_time_axis(ax, comp_data.index, time_range="auto")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison figure saved to {save_path}")

    return fig
