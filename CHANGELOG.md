# Changelog

All notable changes to the Support Medic Assistant Tool will be documented in this file.

## v1.4 (2025-11-28)

### New Features

- **OOM Investigation** (Database Troubleshooting → Option 9)
  - Automatic analysis of database metrics (size, executions, active workflows)
  - Top workflows by execution count (last 24h)
  - Workflows with recent errors (last 24h)
  - Execution queue status (pending/waiting/running)
  - Execution growth over last 7 days
  - "Likely culprits" analysis with actionable recommendations
    - High execution volume detection (>500 executions/24h)
    - Pending backlog warning (>100 pending)
    - Large database detection (>200 MB)
    - Error-prone workflow identification (>50 errors/24h)
  - kubectl commands for manual Grafana/log investigation

### Technical Changes

- Added `run_db_query_rows()` helper method for multi-row SQL queries
- Added `print_section_header()` helper method for formatted output
- Database troubleshooting menu now has 11 options (moved "Back to main menu" to option 11)

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
