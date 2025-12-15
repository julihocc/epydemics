# Create GitHub Issues for Measles Integration
# Run this script from the repository root

Write-Host "Creating GitHub Issues for Measles Integration..." -ForegroundColor Cyan

# Check if gh CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI (gh) is not installed." -ForegroundColor Red
    Write-Host "Install from: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Check if authenticated
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not authenticated with GitHub CLI." -ForegroundColor Red
    Write-Host "Run: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ GitHub CLI is installed and authenticated" -ForegroundColor Green

# Create milestone
Write-Host "`nCreating milestone..." -ForegroundColor Cyan
try {
    gh api repos/:owner/:repo/milestones -f title="Measles Integration v0.9.1" -f description="Verify measles integration and update notebooks to reflect v0.9.0 native annual support" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Created milestone: Measles Integration v0.9.1" -ForegroundColor Green
        $milestone = "Measles Integration v0.9.1"
    }
    else {
        Write-Host "! Milestone may already exist, continuing..." -ForegroundColor Yellow
        $milestone = "Measles Integration v0.9.1"
    }
}
catch {
    Write-Host "! Could not create milestone, continuing without it..." -ForegroundColor Yellow
    $milestone = ""
}

# Function to create issue
function Create-Issue {
    param(
        [string]$Title,
        [string]$Body,
        [string[]]$Labels,
        [string]$Milestone
    )
    
    $labelArgs = $Labels | ForEach-Object { "-l", $_ }
    $milestoneArg = if ($Milestone) { @("-m", $Milestone) } else { @() }
    
    try {
        gh issue create --title $Title --body $Body @labelArgs @milestoneArg 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Created: $Title" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "  ✗ Failed to create: $Title" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "  ✗ Failed to create: $Title" -ForegroundColor Red
        return $false
    }
}

Write-Host "`nCreating Phase 1 issues (Verification)..." -ForegroundColor Cyan

# Issue 1
$issue1 = Create-Issue `
    -Title "Verify AnnualFrequencyHandler works correctly" `
    -Body @"
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
"@ `
    -Labels @("verification", "testing", "priority:high") `
    -Milestone $milestone

# Issue 2
$issue2 = Create-Issue `
    -Title "Verify complete measles data workflow" `
    -Body @"
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
- Forecast produces reasonable values (non-negative, within expected range)
- Visualizations render correctly
"@ `
    -Labels @("verification", "integration", "priority:high") `
    -Milestone $milestone

# Issue 3
$issue3 = Create-Issue `
    -Title "Create verification results documentation" `
    -Body @"
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

## Depends On
- #$issue1
- #$issue2
"@ `
    -Labels @("documentation", "verification") `
    -Milestone $milestone

Write-Host "`nCreating Phase 2 issues (Notebook Updates)..." -ForegroundColor Cyan

# Issue 4
$issue4 = Create-Issue `
    -Title "Create new notebook demonstrating native annual support" `
    -Body @"
Replace the obsolete ``06_annual_measles_workaround.ipynb`` with a new notebook demonstrating v0.9.0's native annual frequency support.

**Current State**: Notebook 06 references v0.9.0 as "future" and demonstrates workarounds that are no longer needed.

## Tasks
- [ ] Create ``06_annual_measles_native.ipynb``
- [ ] Add introduction explaining native annual support in v0.9.0
- [ ] Load annual measles data (OWID or simulated)
- [ ] Demonstrate auto-frequency detection
- [ ] Show explicit ``frequency='YE'`` usage
- [ ] Fit model, forecast, and visualize
- [ ] Compare with daily data workflow
- [ ] Highlight: no reindexing, native frequency preserved
- [ ] Test execution end-to-end
- [ ] Delete old ``06_annual_measles_workaround.ipynb``

## Acceptance Criteria
- New notebook executes without errors
- Clearly demonstrates native annual support
- Old workaround notebook is removed
"@ `
    -Labels @("documentation", "notebooks", "priority:high") `
    -Milestone $milestone

# Issue 5
$issue5 = Create-Issue `
    -Title "Remove outdated version references from notebook 07" `
    -Body @"
Update ``07_incidence_mode_measles.ipynb`` to remove version-specific references.

## Tasks
- [ ] Change "Epydemics v0.9.0" to "Epydemics - Incidence Mode Demo"
- [ ] Verify data generation (35 years is sufficient)
- [ ] Test execution
- [ ] Check for other version references

## Acceptance Criteria
- No version-specific language in notebook
- Notebook executes successfully
"@ `
    -Labels @("documentation", "notebooks", "priority:medium") `
    -Milestone $milestone

# Issue 6
$issue6 = Create-Issue `
    -Title "Remove outdated version references from all notebooks" `
    -Body @"
Search all notebooks for references to v0.9.0 as "future", "planned", "workaround", etc.

## Notebooks to check
- ``scenario_analysis_measles.ipynb``
- ``validation_usa_measles.ipynb``
- ``01_sird_basic_workflow.ipynb``
- ``02_sirdv_vaccination_analysis.ipynb``
- ``03_global_covid19_forecasting.ipynb``
- ``04_parallel_simulations.ipynb``
- ``05_multi_backend_comparison.ipynb``

## Search terms
- "v0.9.0" (as future reference)
- "planned"
- "future"
- "workaround"
- "NOT AVAILABLE YET"

## Tasks
- [ ] Search for outdated references
- [ ] Update or remove outdated language
- [ ] Ensure consistency in terminology
- [ ] Test all notebooks with ``run_all_notebooks.py``

## Acceptance Criteria
- No misleading version references
- Consistent terminology across notebooks
"@ `
    -Labels @("documentation", "notebooks", "priority:medium") `
    -Milestone $milestone

Write-Host "`nCreating Phase 3 issues (Integration Testing)..." -ForegroundColor Cyan

# Issue 7
$issue7 = Create-Issue `
    -Title "Execute full notebook test suite" `
    -Body @"
Run the automated test harness on all notebooks to verify they execute correctly.

## Tasks
- [ ] Run ``python examples/run_all_notebooks.py``
- [ ] Document pass/fail status for each notebook
- [ ] Investigate and fix any failures
- [ ] Update test harness if needed

## Acceptance Criteria
- All notebooks pass automated tests (or failures are documented)
- Test results are recorded

## Depends On
- #$issue4
- #$issue5
- #$issue6
"@ `
    -Labels @("testing", "notebooks", "priority:high") `
    -Milestone $milestone

# Issue 8
$issue8 = Create-Issue `
    -Title "Manually verify all notebooks in Jupyter" `
    -Body @"
Open each notebook in Jupyter and execute cell-by-cell to verify interactive experience.

## Tasks
- [ ] Test each notebook interactively
- [ ] Verify visualizations render correctly
- [ ] Check for deprecation warnings
- [ ] Verify markdown formatting
- [ ] Test on clean environment

## Acceptance Criteria
- All notebooks work in interactive Jupyter environment
- No unexpected warnings or errors
"@ `
    -Labels @("testing", "notebooks", "priority:medium") `
    -Milestone $milestone

# Issue 9
$issue9 = Create-Issue `
    -Title "Test measles data download scripts" `
    -Body @"
Verify that data fetching scripts work correctly.

## Tasks
- [ ] Test ``examples/data/fetch_measles_data.py``
- [ ] Verify CSV files download correctly
- [ ] Confirm path resolution works in notebooks
- [ ] Test from different working directories

## Acceptance Criteria
- Data downloads successfully
- Notebooks can find downloaded data
"@ `
    -Labels @("testing", "data", "priority:medium") `
    -Milestone $milestone

Write-Host "`nCreating Phase 4 issues (Release Decision)..." -ForegroundColor Cyan

# Issue 10
$issue10 = Create-Issue `
    -Title "Decide if release is needed (v0.9.1 vs v0.10.0)" `
    -Body @"
Based on verification results, determine if a new release is warranted and what version number.

## Decision Tree
- **Only notebook updates** → No version bump
- **Bug fixes in annual handling** → v0.9.1 (patch)
- **New features/enhancements** → v0.10.0 (minor)
- **Breaking changes** → v1.0.0 or v0.10.0

## Tasks
- [ ] Review verification results
- [ ] Assess scope of changes
- [ ] Determine version number
- [ ] Document decision rationale

## Acceptance Criteria
- Clear decision on whether to release
- Version number determined (if releasing)

## Depends On
- #$issue3
- #$issue7
"@ `
    -Labels @("release", "decision", "priority:high") `
    -Milestone $milestone

# Issue 11
$issue11 = Create-Issue `
    -Title "Prepare v0.9.1 release" `
    -Body @"
If release is needed, prepare all release artifacts.

## Tasks
- [ ] Update ``CHANGELOG.md``
- [ ] Update version in ``pyproject.toml``
- [ ] Update version in ``src/epydemics/__init__.py``
- [ ] Run full test suite: ``pytest``
- [ ] Build package: ``python -m build``
- [ ] Test install: ``pip install dist/epydemics-X.X.X.tar.gz``
- [ ] Create git tag: ``git tag vX.X.X``
- [ ] Push tag: ``git push origin vX.X.X``
- [ ] Create GitHub release with notes
- [ ] Upload to PyPI: ``twine upload dist/*``

## Acceptance Criteria
- All release artifacts created
- Package published to PyPI
- GitHub release created

## Depends On
- #$issue10
"@ `
    -Labels @("release", "priority:high") `
    -Milestone $milestone

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Issue Creation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nCreated 11 issues for Measles Integration project" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Create a GitHub Project to organize these issues" -ForegroundColor White
Write-Host "2. Run: gh project create --owner julihocc --title 'Measles Integration v0.9.1'" -ForegroundColor Cyan
Write-Host "3. Add issues to the project via GitHub web UI" -ForegroundColor White
Write-Host "`nOr visit: https://github.com/julihocc/epydemics/issues" -ForegroundColor Cyan
