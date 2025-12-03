# Changelog

All notable changes to the Support Medic Assistant Tool will be documented in this file.

## v1.4.1 (2025-11-28)

### Menu Reorganization

- **Main Menu Restructured** - Replaced flat menu with 7 category submenus:
  - Health & Diagnostics (health check, execution status, storage diagnostics)
  - Workflow Operations (export, import, deactivate)
  - Execution Management (check, cancel, clear queued)
  - Database & Storage (backup, troubleshooting, prune binary data)
  - User & Access (2FA, owner email)
  - Logs (view, download)
  - Settings (workspace/cluster, redeploy)
- **Pre-Menu Enhancement** - Added quit option ('q') to operation mode selection
- All submenus support 'b' to go back to main menu

### New Features

- **Storage Diagnostics** (Health & Diagnostics → Option 3)
  - Disk usage analysis
  - Database size with table breakdown
  - Execution counts by status and last 7 days
  - Binary data analysis with size metrics
  - Top workflows by stored data (active vs inactive)
  - Intelligent recommendations for storage cleanup

- **Clear Queued Executions** (Execution Management → Option 4)
  - Clear all executions with status='new'
  - Preview up to 5 queued executions before clearing
  - Automatic backup before operation
  - Verification after clearing

- **Prune Binary Data** (Database & Storage → Option 3)
  - Trigger bfp-9000 sidecar to prune old execution data
  - Shows current binary data usage before pruning
  - Sends SIGUSR1 signal to bfp-9000 container
  - Background operation with progress monitoring guidance

### Improvements

- Better menu organization for easier navigation
- Category-based grouping of related operations
- Consistent 'b' back option across all submenus
- Pod requirement checks in each submenu

---

## v1.4 (2025-11-28)

### New Features

- **OOM Investigation with Report Generation** (Database Troubleshooting → Option 9)
  - **Deep Database Analysis:**
    - Database metrics (size, executions, active workflows)
    - Table size breakdown with bloat detection
    - Largest executions by data size
    - Workflows with most stored data (active vs inactive)
    - Top workflows by execution count (last 24h)
    - Workflows with recent errors (last 24h)
    - Execution queue status (pending/waiting/running)
    - Execution growth trends (last 7 days)
  - **Intelligent Analysis:**
    - "Likely culprits" identification with thresholds:
      - Table bloat detection (execution_data > 100MB)
      - Inactive workflow data (> 10MB inactive workflows)
      - Large individual executions (> 10MB each)
      - Pending backlog warning (> 100 pending)
      - Large database (> 200MB)
    - Actionable recommendations for each issue
  - **Report Generation:**
    - Downloadable Markdown report to ~/Downloads
    - Comprehensive findings summary
    - SQL commands for data pruning
    - kubectl commands for manual investigation
    - Customer-facing recommendations

### Technical Changes

- Added `run_db_query_rows()` helper method for multi-row SQL queries
- Added `print_section_header()` helper method for formatted output
- Added `format_bytes()` for human-readable size formatting
- Added database analysis methods:
  - `get_database_size()` - Get database file size
  - `get_table_sizes()` - Table size breakdown (uses dbstat with fallback)
  - `get_largest_executions()` - Find largest execution data
  - `get_workflow_data_sizes()` - Total stored data per workflow
  - `get_top_workflows_24h()` - Top workflows by execution count
  - `get_error_workflows_24h()` - Error-prone workflows
  - `get_execution_growth()` - 7-day execution trends
- Added analysis methods:
  - `analyze_oom_culprits()` - Intelligent root cause analysis
  - `print_recommended_actions()` - Display actionable recommendations
  - `generate_oom_report()` - Create downloadable Markdown report
- Database troubleshooting menu now has 11 options (moved "Back to main menu" to option 11)

### Bug Fixes

- Fixed SQL escaping issues in complex queries (removed incorrect shell escaping)
- Fixed `run_db_query_rows()` invalid parameter error

---

## v1.3 (2025-11-25)

### New Features

- **Pre-Menu for Operation Mode Selection**
  - Choose between full medic operations or deleted instance recovery
  - Cleaner user flow for different use cases

- **Deleted Instance Recovery Menu**
  - List available backups for deleted instances
  - Export workflows from latest backup
  - Export workflows from specific backup
  - Backups retained for 90 days after deletion

### Bug Fixes

- **Pod-required operations check**: Operations requiring a pod now show clear error when Pod: None
  - Lists available operations without pod (export from backup, change workspace)
  - Prevents cryptic errors when trying to run operations without a pod

- **Export workflows validation**: Live instance export now validates success/failure
  - Checks for error messages in exported files
  - Cleans up failed exports automatically

### Improvements

- Better user guidance for workspace recovery scenarios
- Clearer error messages when backups not found
- Improved handling of deleted instance workflows

---

## v1.2.2 (2025-11-24) - Hotfix

### Bug Fixes
- **Change workspace/cluster**: Fixed graceful error handling when pod not found
  - Previously: Tool entered broken state with `Pod: None`, all operations failed
  - Now: Offers recovery options:
    - Try different workspace/cluster
    - Revert to previous working workspace
    - Continue with limited operations (backup export only)
  - Added state rollback to preserve working configuration
  - Added helpful error messages explaining why pod might not be found

### Improvements
- Better user experience when switching to invalid/non-existent workspaces
- Prevents tool from entering unusable state
- Clear guidance on available operations without a pod
- New `find_pod()` helper method for cleaner code

---

## v1.2.1 (2025-11-21) - Hotfix

### Bug Fixes
- **Export from backup**: Fixed filename to use backup's date instead of today's date
  - Previously: Downloading backup from Nov 17 would save as `workspace-backup-2025-11-21.zip`
  - Now: Correctly saves as `workspace-backup-2025-11-17.zip`
  - Users can now accurately identify which backup they downloaded

---

## v1.2 (2024-11-21)

### New Features

- **Execution Status Checker** - Detailed analysis of executions by status
  - Waiting executions with "year 3000" detection
  - Pending/new execution analysis
  - Running execution monitoring
  - Error analysis and breakdown
  - All statuses summary view

- **Log Download Menu** - Download various log types
  - n8n container logs (multiple timeframe options)
  - backup-cron logs
  - Kubernetes events and pod descriptions
  - Execution logs by ID
  - All logs bundle (tar.gz)

- **Disable 2FA** - Disable multi-factor authentication
  - Email validation
  - Confirmation prompts
  - Shows cloudbot notify command

- **Change Owner Email** - Update workspace owner
  - Identity verification checklist
  - Email conflict detection
  - Plus addressing support
  - Automatic backup before change
  - Verification after update

### Documentation

- Sanitized all examples (no real customer data)
- Added privacy & security notice
- Updated README with new features
- Updated QUICK_START guide
- Created CHANGELOG.md

### Bug Fixes

- Improved error handling for database queries
- Better feedback for failed operations
- Clearer instructions for next steps

### Testing

- Verified 2FA disable functionality
- Verified owner email change process
- Confirmed log downloads work correctly

---

## v1.1 (2024-11-17)

### New Features

- **VPN Connection Reminder** - Shows warning at startup
- **Simplified Cluster Input** - Just enter number (e.g., "48" instead of "prod-users-gwc-48")
- **Database Troubleshooting Menu** - Guided pre-built queries for common issues
- **Health Check** - Quick status overview (Option 0)

### Improvements

- Better error handling for database queries
- Auto-retry option for failed queries
- Clearer error messages with possible causes

---

## v1.0 (2024-11-15)

### Initial Release

- Interactive menu-driven interface
- Auto-discovery of pod names
- Automatic downloads to ~/Downloads folder
- Safety confirmations for destructive operations
- Colour-coded output for better readability
- Database backup before modifications

### Features

- Export workflows (live instance)
- Export workflows (from backup)
- Import workflows
- Deactivate all workflows
- Deactivate specific workflow
- Check execution by ID
- Cancel pending executions
- Cancel waiting executions
- Take backup
- View recent logs
- Database shell access
- Redeploy instance (cloudbot command)
- Change workspace/cluster
