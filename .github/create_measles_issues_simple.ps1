# Create GitHub Issues for Measles Integration (Simplified)
# Run this script from the repository root

Write-Host "Creating GitHub Issues for Measles Integration..." -ForegroundColor Cyan

# Check if gh CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI (gh) is not installed." -ForegroundColor Red
    exit 1
}

Write-Host "✓ GitHub CLI is installed" -ForegroundColor Green

# Function to create issue (without labels)
function Create-Issue {
    param(
        [string]$Title,
        [string]$Body
    )
    
    try {
        $output = gh issue create --title $Title --body $Body 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Created: $Title" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "  ✗ Failed: $Title" -ForegroundColor Red
            Write-Host "    Error: $output" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "  ✗ Failed: $Title - $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "`nCreating Phase 1 issues (Verification)..." -ForegroundColor Cyan

# Issue 1
Create-Issue `
    -Title "[Phase 1] Verify AnnualFrequencyHandler works correctly" `
    -Body @"
**Labels**: verification, testing, priority:high  
**Milestone**: Measles Integration v0.9.1

Verify that the ``AnnualFrequencyHandler`` implemented in v0.9.0 works correctly with real-world annual data.

## Tasks
- [ ] Create test script: ``examples/test_annual_native.py``
- [ ] Load measles data with annual frequency (YE)
- [ ] Verify ``DataContainer`` auto-detects ``YE`` frequency
- [ ] Confirm no reindexing occurs (native frequency preserved)
- [ ] Test both incidence and cumulative modes
- [ ] Verify ``max_lag=3`` default is applied
- [ ] Check logs show "Using AnnualFrequencyHandler"

## Acceptance Criteria
- Script executes without errors
- Logs confirm AnnualFrequencyHandler is used
- Annual frequency is preserved (no reindexing to daily)
"@

# Issue 2
Create-Issue `
    -Title "[Phase 1] Verify complete measles data workflow" `
    -Body @"
**Labels**: verification, integration, priority:high  
**Milestone**: Measles Integration v0.9.1

Test the complete pipeline from data loading to forecasting with annual measles data.

## Tasks
- [ ] Run ``examples/data/fetch_measles_data.py``
- [ ] Load USA measles data (annual, incidence mode)
- [ ] Create ``DataContainer`` with auto-detection
- [ ] Fit VAR model with default parameters
- [ ] Generate forecast (5-10 years ahead)
- [ ] Visualize results
- [ ] Document any errors or warnings

## Acceptance Criteria
- Complete workflow executes successfully
- Forecast produces reasonable values
- Visualizations render correctly
"@

# Issue 3
Create-Issue `
    -Title "[Phase 1] Create verification results documentation" `
    -Body @"
**Labels**: documentation, verification  
**Milestone**: Measles Integration v0.9.1

Document findings from annual frequency handler and measles pipeline testing.

## Tasks
- [ ] Create ``VERIFICATION_RESULTS.md``
- [ ] Document test outcomes (pass/fail)
- [ ] Note any bugs or limitations discovered
- [ ] Identify gaps between implementation and documentation
- [ ] Recommend next steps based on findings

## Acceptance Criteria
- Clear documentation of what works and what doesn't
- Actionable recommendations for fixes (if needed)
"@

Write-Host "`nCreating Phase 2 issues (Notebook Updates)..." -ForegroundColor Cyan

# Issue 4
Create-Issue `
    -Title "[Phase 2] Create new notebook demonstrating native annual support" `
    -Body @"
**Labels**: documentation, notebooks, priority:high  
**Milestone**: Measles Integration v0.9.1

Replace the obsolete ``06_annual_measles_workaround.ipynb`` with a new notebook demonstrating v0.9.0's native annual frequency support.

## Tasks
- [ ] Create ``06_annual_measles_native.ipynb``
- [ ] Add introduction explaining native annual support in v0.9.0
- [ ] Load annual measles data (OWID or simulated)
- [ ] Demonstrate auto-frequency detection
- [ ] Show explicit ``frequency='YE'`` usage
- [ ] Fit model, forecast, and visualize
- [ ] Test execution end-to-end
- [ ] Delete old ``06_annual_measles_workaround.ipynb``

## Acceptance Criteria
- New notebook executes without errors
- Clearly demonstrates native annual support
- Old workaround notebook is removed
"@

# Issue 5
Create-Issue `
    -Title "[Phase 2] Remove outdated version references from notebook 07" `
    -Body @"
**Labels**: documentation, notebooks, priority:medium  
**Milestone**: Measles Integration v0.9.1

Update ``07_incidence_mode_measles.ipynb`` to remove version-specific references.

## Tasks
- [ ] Change "Epydemics v0.9.0" to "Epydemics - Incidence Mode Demo"
- [ ] Verify data generation (35 years is sufficient)
- [ ] Test execution

## Acceptance Criteria
- No version-specific language in notebook
- Notebook executes successfully
"@

# Issue 6
Create-Issue `
    -Title "[Phase 2] Audit all notebooks for outdated references" `
    -Body @"
**Labels**: documentation, notebooks, priority:medium  
**Milestone**: Measles Integration v0.9.1

Search all notebooks for references to v0.9.0 as "future", "planned", "workaround", etc.

## Notebooks to check
- ``scenario_analysis_measles.ipynb``
- ``validation_usa_measles.ipynb``
- ``01_sird_basic_workflow.ipynb``
- ``02_sirdv_vaccination_analysis.ipynb``
- ``03_global_covid19_forecasting.ipynb``
- ``04_parallel_simulations.ipynb``
- ``05_multi_backend_comparison.ipynb``

## Tasks
- [ ] Search for outdated references
- [ ] Update or remove outdated language
- [ ] Ensure consistency in terminology
- [ ] Test all notebooks with ``run_all_notebooks.py``

## Acceptance Criteria
- No misleading version references
- Consistent terminology across notebooks
"@

Write-Host "`nCreating Phase 3 issues (Integration Testing)..." -ForegroundColor Cyan

# Issue 7
Create-Issue `
    -Title "[Phase 3] Execute full notebook test suite" `
    -Body @"
**Labels**: testing, notebooks, priority:high  
**Milestone**: Measles Integration v0.9.1

Run the automated test harness on all notebooks to verify they execute correctly.

## Tasks
- [ ] Run ``python examples/run_all_notebooks.py``
- [ ] Document pass/fail status for each notebook
- [ ] Investigate and fix any failures
- [ ] Update test harness if needed

## Acceptance Criteria
- All notebooks pass automated tests (or failures are documented)
- Test results are recorded
"@

# Issue 8
Create-Issue `
    -Title "[Phase 3] Manually verify all notebooks in Jupyter" `
    -Body @"
**Labels**: testing, notebooks, priority:medium  
**Milestone**: Measles Integration v0.9.1

Open each notebook in Jupyter and execute cell-by-cell to verify interactive experience.

## Tasks
- [ ] Test each notebook interactively
- [ ] Verify visualizations render correctly
- [ ] Check for deprecation warnings
- [ ] Verify markdown formatting

## Acceptance Criteria
- All notebooks work in interactive Jupyter environment
- No unexpected warnings or errors
"@

# Issue 9
Create-Issue `
    -Title "[Phase 3] Test measles data download scripts" `
    -Body @"
**Labels**: testing, data, priority:medium  
**Milestone**: Measles Integration v0.9.1

Verify that data fetching scripts work correctly.

## Tasks
- [ ] Test ``examples/data/fetch_measles_data.py``
- [ ] Verify CSV files download correctly
- [ ] Confirm path resolution works in notebooks

## Acceptance Criteria
- Data downloads successfully
- Notebooks can find downloaded data
"@

Write-Host "`nCreating Phase 4 issues (Release Decision)..." -ForegroundColor Cyan

# Issue 10
Create-Issue `
    -Title "[Phase 4] Decide if release is needed (v0.9.1 vs v0.10.0)" `
    -Body @"
**Labels**: release, decision, priority:high  
**Milestone**: Measles Integration v0.9.1

Based on verification results, determine if a new release is warranted and what version number.

## Decision Tree
- **Only notebook updates** → No version bump
- **Bug fixes in annual handling** → v0.9.1 (patch)
- **New features/enhancements** → v0.10.0 (minor)

## Tasks
- [ ] Review verification results
- [ ] Assess scope of changes
- [ ] Determine version number
- [ ] Document decision rationale

## Acceptance Criteria
- Clear decision on whether to release
- Version number determined (if releasing)
"@

# Issue 11
Create-Issue `
    -Title "[Phase 4] Prepare release (if needed)" `
    -Body @"
**Labels**: release, priority:high  
**Milestone**: Measles Integration v0.9.1

If release is needed, prepare all release artifacts.

## Tasks
- [ ] Update ``CHANGELOG.md``
- [ ] Update version in ``pyproject.toml``
- [ ] Update version in ``src/epydemics/__init__.py``
- [ ] Run full test suite: ``pytest``
- [ ] Build package: ``python -m build``
- [ ] Test install locally
- [ ] Create git tag
- [ ] Create GitHub release with notes
- [ ] Upload to PyPI

## Acceptance Criteria
- All release artifacts created
- Package published to PyPI
- GitHub release created
"@

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Issue Creation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Visit: https://github.com/julihocc/epydemics/issues" -ForegroundColor Cyan
Write-Host "2. Add labels to issues manually" -ForegroundColor White
Write-Host "3. Create a GitHub Project to organize them" -ForegroundColor White
Write-Host "4. Add issues to the project" -ForegroundColor White
