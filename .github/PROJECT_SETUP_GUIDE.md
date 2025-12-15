# GitHub Project Setup Guide

## Issues Created ✓

All 11 issues have been successfully created in the repository:

- <https://github.com/julihocc/epydemics/issues>

## Next Steps

### 1. Create Labels (via Web UI)

Visit: <https://github.com/julihocc/epydemics/labels>

Create the following labels:

| Label | Color | Description |
|-------|-------|-------------|
| `verification` | `#0075ca` | Testing and validation work |
| `documentation` | `#0075ca` | Documentation updates |
| `notebooks` | `#7057ff` | Jupyter notebook related |
| `testing` | `#d73a4a` | Integration testing |
| `release` | `#008672` | Release preparation |
| `priority:high` | `#d93f0b` | Critical path items |
| `priority:medium` | `#fbca04` | Important but not blocking |
| `priority:low` | `#0e8a16` | Nice to have |
| `integration` | `#1d76db` | End-to-end integration |
| `data` | `#5319e7` | Data-related tasks |
| `decision` | `#d4c5f9` | Requires decision |

### 2. Add Labels to Issues

For each issue, add the appropriate labels mentioned in the issue description.

**Quick reference**:

- Issues #1-3 (Phase 1): `verification`, `testing`/`integration`/`documentation`, `priority:high`
- Issues #4-6 (Phase 2): `documentation`, `notebooks`, `priority:high`/`medium`
- Issues #7-9 (Phase 3): `testing`, `notebooks`/`data`, `priority:high`/`medium`
- Issues #10-11 (Phase 4): `release`, `decision`/`priority:high`

### 3. Create GitHub Project

**Option A: Using GitHub CLI**

```powershell
gh project create --owner julihocc --title "Measles Integration v0.9.1" --body "Verify measles integration and update notebooks to reflect v0.9.0 native annual support"
```

**Option B: Using Web UI**

1. Go to: <https://github.com/julihocc/epydemics/projects>
2. Click "New project"
3. Choose "Board" template
4. Name: "Measles Integration v0.9.1"
5. Description: "Verify measles integration and update notebooks to reflect v0.9.0 native annual support"

### 4. Add Issues to Project

**Via Web UI**:

1. Open the project
2. Click "+ Add item"
3. Search for issues by phase (e.g., "[Phase 1]")
4. Add all 11 issues

### 5. Organize Project Board

Create the following columns:

1. **📋 Backlog** - Not started
2. **🚧 In Progress** - Currently working
3. **👀 Review** - Needs review
4. **✅ Done** - Completed

Move issues to appropriate columns based on current status.

### 6. Create Milestone (Optional)

If you want to track progress with a milestone:

```powershell
gh api repos/julihocc/epydemics/milestones -f title="Measles Integration v0.9.1" -f description="Verify measles integration and update notebooks" -f due_on="2025-12-22T00:00:00Z"
```

Then assign all issues to this milestone via the web UI.

## Recommended Workflow

1. **Start with Phase 1** (Verification)
   - Complete issues #1-3 first
   - This validates the implementation

2. **Then Phase 2** (Notebook Updates)
   - Update notebooks based on verification results
   - Issues #4-6

3. **Then Phase 3** (Testing)
   - Verify all changes work
   - Issues #7-9

4. **Finally Phase 4** (Release Decision)
   - Decide if release is needed
   - Issues #10-11

## Quick Links

- **Issues**: <https://github.com/julihocc/epydemics/issues>
- **Projects**: <https://github.com/julihocc/epydemics/projects>
- **Labels**: <https://github.com/julihocc/epydemics/labels>
- **Milestones**: <https://github.com/julihocc/epydemics/milestones>
