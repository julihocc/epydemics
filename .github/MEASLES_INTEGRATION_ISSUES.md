# GitHub Issues for Measles Integration

## Phase 1: Verification

### Issue 1: Test Annual Frequency Handler

**Title**: Verify AnnualFrequencyHandler works correctly  
**Labels**: `verification`, `testing`, `priority:high`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Verify that the `AnnualFrequencyHandler` implemented in v0.9.0 works correctly with real-world annual data.

**Tasks**:

- [ ] Create test script: `examples/test_annual_native.py`
- [ ] Load measles data with annual frequency (YE)
- [ ] Verify `DataContainer` auto-detects `YE` frequency
- [ ] Confirm no reindexing occurs (native frequency preserved)
- [ ] Test both incidence and cumulative modes
- [ ] Verify `max_lag=3` default is applied
- [ ] Check logs show "Using AnnualFrequencyHandler"

**Acceptance Criteria**:

- Script executes without errors
- Logs confirm AnnualFrequencyHandler is used
- Annual frequency is preserved (no reindexing to daily)

---

### Issue 2: Test End-to-End Measles Pipeline

**Title**: Verify complete measles data workflow  
**Labels**: `verification`, `integration`, `priority:high`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Test the complete pipeline from data loading to forecasting with annual measles data.

**Tasks**:

- [ ] Run `examples/data/fetch_measles_data.py`
- [ ] Load USA measles data (annual, incidence mode)
- [ ] Create `DataContainer` with auto-detection
- [ ] Fit VAR model with default parameters
- [ ] Generate forecast (5-10 years ahead)
- [ ] Visualize results
- [ ] Document any errors or warnings

**Acceptance Criteria**:

- Complete workflow executes successfully
- Forecast produces reasonable values (non-negative, within expected range)
- Visualizations render correctly

---

### Issue 3: Document Verification Results

**Title**: Create verification results documentation  
**Labels**: `documentation`, `verification`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Document findings from annual frequency handler and measles pipeline testing.

**Tasks**:

- [ ] Create `VERIFICATION_RESULTS.md`
- [ ] Document test outcomes (pass/fail)
- [ ] Note any bugs or limitations discovered
- [ ] Identify gaps between implementation and documentation
- [ ] Recommend next steps based on findings

**Acceptance Criteria**:

- Clear documentation of what works and what doesn't
- Actionable recommendations for fixes (if needed)

---

## Phase 2: Notebook Updates

### Issue 4: Replace Notebook 06 with Native Annual Support Demo

**Title**: Create new notebook demonstrating native annual support  
**Labels**: `documentation`, `notebooks`, `priority:high`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Replace the obsolete `06_annual_measles_workaround.ipynb` with a new notebook demonstrating v0.9.0's native annual frequency support.

**Current State**: Notebook 06 references v0.9.0 as "future" and demonstrates workarounds that are no longer needed.

**Tasks**:

- [ ] Create `06_annual_measles_native.ipynb`
- [ ] Add introduction explaining native annual support in v0.9.0
- [ ] Load annual measles data (OWID or simulated)
- [ ] Demonstrate auto-frequency detection
- [ ] Show explicit `frequency='YE'` usage
- [ ] Fit model, forecast, and visualize
- [ ] Compare with daily data workflow
- [ ] Highlight: no reindexing, native frequency preserved
- [ ] Test execution end-to-end
- [ ] Delete old `06_annual_measles_workaround.ipynb`

**Acceptance Criteria**:

- New notebook executes without errors
- Clearly demonstrates native annual support
- Old workaround notebook is removed

---

### Issue 5: Update Notebook 07 Version References

**Title**: Remove outdated version references from notebook 07  
**Labels**: `documentation`, `notebooks`, `priority:medium`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Update `07_incidence_mode_measles.ipynb` to remove version-specific references.

**Tasks**:

- [ ] Change "Epydemics v0.9.0" to "Epydemics - Incidence Mode Demo"
- [ ] Verify data generation (35 years is sufficient)
- [ ] Test execution
- [ ] Check for other version references

**Acceptance Criteria**:

- No version-specific language in notebook
- Notebook executes successfully

---

### Issue 6: Audit All Notebooks for Outdated References

**Title**: Remove outdated version references from all notebooks  
**Labels**: `documentation`, `notebooks`, `priority:medium`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Search all notebooks for references to v0.9.0 as "future", "planned", "workaround", etc.

**Notebooks to check**:

- `scenario_analysis_measles.ipynb`
- `validation_usa_measles.ipynb`
- `01_sird_basic_workflow.ipynb`
- `02_sirdv_vaccination_analysis.ipynb`
- `03_global_covid19_forecasting.ipynb`
- `04_parallel_simulations.ipynb`
- `05_multi_backend_comparison.ipynb`

**Search terms**:

- "v0.9.0" (as future reference)
- "planned"
- "future"
- "workaround"
- "NOT AVAILABLE YET"

**Tasks**:

- [ ] Search for outdated references
- [ ] Update or remove outdated language
- [ ] Ensure consistency in terminology
- [ ] Test all notebooks with `run_all_notebooks.py`

**Acceptance Criteria**:

- No misleading version references
- Consistent terminology across notebooks

---

## Phase 3: Integration Testing

### Issue 7: Run Automated Notebook Test Suite

**Title**: Execute full notebook test suite  
**Labels**: `testing`, `notebooks`, `priority:high`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Run the automated test harness on all notebooks to verify they execute correctly.

**Tasks**:

- [ ] Run `python examples/run_all_notebooks.py`
- [ ] Document pass/fail status for each notebook
- [ ] Investigate and fix any failures
- [ ] Update test harness if needed

**Acceptance Criteria**:

- All notebooks pass automated tests (or failures are documented)
- Test results are recorded

---

### Issue 8: Manual Notebook Verification

**Title**: Manually verify all notebooks in Jupyter  
**Labels**: `testing`, `notebooks`, `priority:medium`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Open each notebook in Jupyter and execute cell-by-cell to verify interactive experience.

**Tasks**:

- [ ] Test each notebook interactively
- [ ] Verify visualizations render correctly
- [ ] Check for deprecation warnings
- [ ] Verify markdown formatting
- [ ] Test on clean environment

**Acceptance Criteria**:

- All notebooks work in interactive Jupyter environment
- No unexpected warnings or errors

---

### Issue 9: Verify Data Fetching Scripts

**Title**: Test measles data download scripts  
**Labels**: `testing`, `data`, `priority:medium`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Verify that data fetching scripts work correctly.

**Tasks**:

- [ ] Test `examples/data/fetch_measles_data.py`
- [ ] Verify CSV files download correctly
- [ ] Confirm path resolution works in notebooks
- [ ] Test from different working directories

**Acceptance Criteria**:

- Data downloads successfully
- Notebooks can find downloaded data

---

## Phase 4: Release Decision

### Issue 10: Assess Changes and Determine Version

**Title**: Decide if release is needed (v0.9.1 vs v0.10.0)  
**Labels**: `release`, `decision`, `priority:high`  
**Milestone**: Measles Integration v0.9.1

**Description**:
Based on verification results, determine if a new release is warranted and what version number.

**Decision Tree**:

- **Only notebook updates** → No version bump
- **Bug fixes in annual handling** → v0.9.1 (patch)
- **New features/enhancements** → v0.10.0 (minor)
- **Breaking changes** → v1.0.0 or v0.10.0

**Tasks**:

- [ ] Review verification results
- [ ] Assess scope of changes
- [ ] Determine version number
- [ ] Document decision rationale

**Acceptance Criteria**:

- Clear decision on whether to release
- Version number determined (if releasing)

---

### Issue 11: Prepare Release (If Needed)

**Title**: Prepare v0.9.1 release  
**Labels**: `release`, `priority:high`  
**Milestone**: Measles Integration v0.9.1  
**Depends on**: Issue #10

**Description**:
If release is needed, prepare all release artifacts.

**Tasks**:

- [ ] Update `CHANGELOG.md`
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `src/epydemics/__init__.py`
- [ ] Run full test suite: `pytest`
- [ ] Build package: `python -m build`
- [ ] Test install: `pip install dist/epydemics-X.X.X.tar.gz`
- [ ] Create git tag: `git tag vX.X.X`
- [ ] Push tag: `git push origin vX.X.X`
- [ ] Create GitHub release with notes
- [ ] Upload to PyPI: `twine upload dist/*`

**Acceptance Criteria**:

- All release artifacts created
- Package published to PyPI
- GitHub release created

---

## Project Organization

**Project Name**: Measles Integration v0.9.1

**Columns**:

1. **Backlog** - Not started
2. **In Progress** - Currently working
3. **Review** - Needs review
4. **Done** - Completed

**Milestones**:

- Measles Integration v0.9.1 (target: 1 week)

**Priority Labels**:

- `priority:high` - Critical path items
- `priority:medium` - Important but not blocking
- `priority:low` - Nice to have

**Type Labels**:

- `verification` - Testing/validation work
- `documentation` - Notebook/doc updates
- `testing` - Integration testing
- `release` - Release preparation
- `bug` - Bug fixes (if discovered)
