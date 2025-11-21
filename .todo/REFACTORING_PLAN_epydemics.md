# Refactoring Plan for `epydemics/epydemics.py`

This plan outlines the steps to refactor the monolithic `epydemics/epydemics.py` file to improve module structure, separation of concerns, and overall architecture.

## Objectives:
- Enhance code readability and maintainability.
- Improve modularity and reusability of components.
- Align with best coding practices and a solid architectural design.

## Proposed Steps:

1.  **Move Constants:**
    -   Remove constant definitions (e.g., `ratios`, `logit_ratios`, `forecasting_levels`, `compartments`, `compartment_labels`, `central_tendency_methods`, `method_names`, `method_colors`) from `epydemics/epydemics.py`.
    -   Add an import statement in `epydemics/epydemics.py` to import these constants from `epydemics.core.constants`.

2.  **Move Exceptions:**
    -   Move the `NotDataFrameError` exception from `epydemics/epydemics.py` to `epydemics/core/exceptions.py`.
    -   Update imports in `epydemics/epydemics.py` and any other affected files to reflect the new location.

3.  **Move Data Processing Functions:**
    -   Relocate functions related to data processing (`prepare_for_logit_function`, `logit_function`, `logistic_function`, `add_logit_ratios`, `validate_data`, `process_data_from_owid`, `preprocess_data`, `reindex_data`, `feature_engineering`) from `epydemics/epydemics.py`.
    -   These functions should be moved to `epydemics/data/container.py` or a newly created `epydemics/data/processing.py` if `container.py` becomes too large or specific to the `DataContainer` class. For now, the initial target is `epydemics/data/container.py`.
    -   Update imports as necessary.

4.  **Move `DataContainer` class:**
    -   Move the `DataContainer` class definition from `epydemics/epydemics.py` to `epydemics/data/container.py`.
    -   Ensure all necessary imports for `DataContainer` are present in `epydemics/data/container.py` and removed from `epydemics/epydemics.py`.

5.  **Move `Model` class:**
    -   Move the `Model` class (and all its associated methods) from `epydemics/epydemics.py` to `epydemics/models/base.py`.
    -   Adjust imports in `epydemics/epydemics.py` and `epydemics/models/base.py` accordingly.

6.  **Move Analysis/Visualization Functions:**
    -   Relocate `visualize_results` function from `epydemics/epydemics.py` to `epydemics/analysis/visualization.py`.
    -   Relocate `evaluate_forecast` function from `epydemics/epydemics.epydemics.py` to `epydemics/analysis/evaluation.py`.
    -   Update imports in all affected files.

7.  **Handle Logging Configuration:**
    -   Review the logging configuration (`logging.basicConfig(...)`) in `epydemics/epydemics.py`.
    -   Decide whether it should be moved to `epydemics/__init__.py` for package-wide configuration, or to a dedicated utility module (e.g., `epydemics/utils/logging.py`), or remain in a main entry point if `epydemics.py` retains that role.

8.  **Clean up `epydemics/epydemics.py`:**
    -   After all functionalities are moved, `epydemics/epydemics.py` should primarily contain package-level imports or remain empty if its purpose is entirely subsumed by other modules.
    -   Remove any unused imports.

9.  **Verification and Testing:**
    -   After each significant move, ensure that existing tests still pass.
    -   Add new unit tests for any functionality that was previously untestable or that has new responsibilities.
    -   Run integration tests to ensure the overall application flow remains intact.

10. **Update Documentation:**
    -   Reflect all changes in module structure, function locations, and class responsibilities within the project's documentation.