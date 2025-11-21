<#
.SYNOPSIS
  Creates a GitHub Project (Projects v2) for the epydemics repository and adds predefined issues.

.DESCRIPTION
  Requires a GitHub CLI authentication token WITH the 'project' scope enabled.
  If your current token lacks the scope, update it first (see GITHUB_PROJECT_SETUP.md).

  Steps performed:
    1. Create Project V2 via GraphQL mutation
    2. Capture returned project id and url
    3. Add existing issues to the project using addProjectV2ItemById mutation

  NOTE: Project V2 items are added by node IDs (GraphQL). This script retrieves each issue's node_id
  via REST (gh api) and then adds it. If creation fails with INSUFFICIENT_SCOPES, refresh token with project scope.

.PARAMETER Title
  Title of the new project. Default: 'Epydemics v1.0 Refactoring Roadmap'

.PARAMETER OwnerLogin
  GitHub username owner of the project. Default: 'julihocc'

.PARAMETER Repo
  Repository name. Default: 'epydemics'

.PARAMETER IssueNumbers
  Array of issue numbers to add. Default: refactoring roadmap set.

.EXAMPLE
  pwsh ./scripts/create_github_project.ps1 -Verbose

.EXAMPLE
  pwsh ./scripts/create_github_project.ps1 -IssueNumbers 10,11,12

.NOTES
  Ensure: gh auth refresh -h github.com -s project
#>
param(
  [string]$Title = 'Epydemics v1.0 Refactoring Roadmap',
  [string]$OwnerLogin = 'julihocc',
  [string]$Repo = 'epydemics',
  [int[]]$IssueNumbers = @(23,24,25,26,27,46,47,48,49,50,51,52,53,54,55,56)
)

# region --- Pre-flight checks ---
Write-Host 'Validating gh CLI availability...' -ForegroundColor Cyan
$ghVersion = (gh --version 2>$null) -join ' '
if (-not $ghVersion) { throw 'GitHub CLI not found in PATH.' }
Write-Host "Found gh: $ghVersion" -ForegroundColor Green

Write-Host 'Checking auth status...' -ForegroundColor Cyan
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) { throw 'gh auth status failed. Please run gh auth login first.' }
Write-Host $authStatus

# endregion

# region --- Resolve owner node id (user) ---
Write-Host 'Resolving owner node id via REST...' -ForegroundColor Cyan
$ownerUser = gh api users/$OwnerLogin --jq '{login: .login, node_id: .node_id}' | ConvertFrom-Json
if (-not $ownerUser.node_id) { throw 'Could not resolve owner node id.' }
$ownerId = $ownerUser.node_id
Write-Host "Owner node id: $ownerId" -ForegroundColor Green
# endregion

# region --- Create Project V2 ---
Write-Host 'Creating Project V2 (GraphQL)...' -ForegroundColor Cyan
$createMutation = @'
mutation($ownerId:ID!, $title:String!) {
  createProjectV2(input: {ownerId: $ownerId, title: $title}) {
    projectV2 { id title url number }
  }
}
'@

$createResp = gh api graphql -f query="$createMutation" -F ownerId=$ownerId -F title="$Title" 2>&1
if ($LASTEXITCODE -ne 0) { Write-Error 'Project creation failed. Ensure token has project scope.'; Write-Host $createResp; exit 1 }
$projectObj = ($createResp | ConvertFrom-Json).data.createProjectV2.projectV2
$projectId = $projectObj.id
Write-Host "Created project: $($projectObj.title)" -ForegroundColor Green
Write-Host "Project URL: $($projectObj.url)" -ForegroundColor Yellow
Write-Host "Project ID: $projectId" -ForegroundColor Yellow
# endregion

# region --- Link project to repository ---
Write-Host 'Linking project to repository...' -ForegroundColor Cyan
$repoInfo = gh api repos/$OwnerLogin/$Repo --jq '{id:.node_id, name:.name, html:.html_url}' | ConvertFrom-Json
if (-not $repoInfo.id) { Write-Warning 'Could not resolve repository node id. Skipping link.' }
else {
  $linkMutation = @'
mutation($projectId:ID!, $repositoryId:ID!){
  linkProjectV2ToRepository(input:{projectId:$projectId, repositoryId:$repositoryId}){ clientMutationId }
}
'@
  $linkResp = gh api graphql -f query="$linkMutation" -F projectId=$projectId -F repositoryId=$($repoInfo.id) 2>&1
  if ($LASTEXITCODE -ne 0) { Write-Warning "Failed to link project to repo $($repoInfo.name). Output: $linkResp" }
  else { Write-Host "Linked project to repository: $($repoInfo.html)" -ForegroundColor Green }
}
# endregion

# region --- Issues to add ---
Write-Host "Preparing to add issues: $($IssueNumbers -join ', ')" -ForegroundColor Cyan

# Retrieve issue node IDs
$issueNodes = @()
foreach ($num in $IssueNumbers) {
  $issueJson = gh api repos/$OwnerLogin/$Repo/issues/$num --jq '{number:.number, node_id:.node_id, title:.title}' 2>$null | ConvertFrom-Json
  if (-not $issueJson.node_id) { Write-Warning "Issue #$num not found or inaccessible."; continue }
  $issueNodes += $issueJson
}

Write-Host "Resolved node IDs for $($issueNodes.Count) issues." -ForegroundColor Green

# GraphQL mutation template for adding items
$addMutation = @'
mutation($projectId:ID!, $contentId:ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item { id }
  }
}
'@

# Add each issue to project
$addedCount = 0
foreach ($issue in $issueNodes) {
  Write-Host "Adding issue #$($issue.number) - $($issue.title)" -ForegroundColor Cyan
  $resp = gh api graphql -f query="$addMutation" -F projectId=$projectId -F contentId=$($issue.node_id) 2>&1
  if ($LASTEXITCODE -ne 0) { Write-Warning "Failed to add issue #$($issue.number). Output: $resp"; continue }
  $addedCount++
  Start-Sleep -Milliseconds 300
}
Write-Host "Added $addedCount / $($issueNodes.Count) issues to project." -ForegroundColor Green
if ($addedCount -lt $issueNodes.Count) {
  Write-Warning 'Some issues failed to add. Review warnings above.'
}
# endregion

Write-Host 'Done. Configure project fields (Status, Iteration, etc.) manually in the GitHub UI.' -ForegroundColor Magenta
