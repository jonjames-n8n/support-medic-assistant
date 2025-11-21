# Changelog

All notable changes to the Support Medic Assistant Tool will be documented in this file.

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
