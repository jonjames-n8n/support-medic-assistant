# Support Medic Tool - Quick Start (v1.4.2)

## Privacy Notice

**Never share real customer data.** All examples use generic placeholders:
- Workspaces: `myworkspace`, `customer-workspace`
- Emails: `user@example.com`

## Install (30 seconds)

```bash
# Download the files to a folder, then:
cd /path/to/downloaded/files
./install.sh

# Choose option 1 for global install
```

## Run

```bash
cloudmedic
```

## Usage Flow

### For Live Instances

1. Select operation mode: **1** (Full medic operations)
2. Enter workspace name (e.g., `myworkspace`)
3. Enter cluster number (e.g., `48` for prod-users-gwc-48)
4. Tool finds pod automatically
5. Select operation from menu
6. Done!

### For Deleted Instances

1. Select operation mode: **2** (Recover workflows from deleted instance)
2. Enter instance name only
3. Choose backup list size (20/50/100/all)
4. Export workflows from backups
5. Done!

## Menu Structure (v1.4.2)

The tool now has **7 organized submenus**:

```
1. Health Check              ← Direct action (runs immediately)
2. Workflow Operations
3. Execution Management
4. Database & Storage
5. User & Access
6. Logs
7. Settings
```

## Most Common Operations

### Quick Reference

| Action | Path | Description |
|--------|------|-------------|
| Health Check | **1** | Quick status overview (direct action) |
| Export workflows | **2** → **1** | Saves to ~/Downloads |
| Export from backup | **2** → **2** | Choose 20/50/100/all backups |
| Deactivate all | **2** → **4** | For crashloops |
| Check execution | **3** → **1** | Check execution error |
| Cancel pending | **3** → **2** | Cancel pending executions |
| Clear queued | **3** → **4** | Clear new executions (v1.4.2) |
| Storage diagnostics | **4** → **2** | Disk, DB, binary data (v1.4.2) |
| OOM Investigation | **4** → **1** → **9** | Deep analysis + report (v1.4) |
| Prune binary data | **4** → **3** | Via bfp-9000 (v1.4.2) |
| Download logs | **6** → **2** | Bundle with all logs |
| Disable 2FA | **5** → **1** | Disable user 2FA |
| Change owner | **5** → **2** | Update owner email |

## Common Workflows

### Handle Crashloop
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 2 (Workflow Operations)
> 4 (Deactivate all)
> y (confirm)
> Run /cloudbot redeploy-instance myworkspace in Slack
```

### Export for Customer (Live Instance)
```bash
cloudmedic
> 1 (Full medic operations)
> customer-workspace
> 52
> 2 (Workflow Operations)
> 1 (Export from live)
> Check ~/Downloads for file
```

### Recover from Deleted Instance (v1.3)
```bash
cloudmedic
> 2 (Recover workflows)
> deleted-workspace
> 1 (List backups)
> 20 (show 20 backups)
> 3 (Export from specific backup)
> 100 (show 100 backups to find old one)
> backup_name_here.tar
> Check ~/Downloads for .zip file
```

### Check Failed Execution
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 3 (Execution Management)
> 1 (Check execution)
> 1234 (execution ID)
> y (view error details)
```

### OOM Investigation (v1.4)
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 4 (Database & Storage)
> 1 (Database troubleshooting)
> 9 (Investigate OOM cause)
> Review analysis
> y (generate report)
> Check ~/Downloads for .md report
```

### Storage Diagnostics (v1.4.2)
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 4 (Database & Storage)
> 2 (Storage diagnostics)
> Review disk, DB, and binary data usage
> Note: If binary data is large, use option 3 to prune
```

### Prune Binary Data (v1.4.2)
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 4 (Database & Storage)
> 3 (Prune binary data)
> Review current usage
> y (confirm pruning)
> Old execution data cleared via bfp-9000
```

### Clear Queued Executions (v1.4.2)
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 3 (Execution Management)
> 4 (Clear queued executions)
> Review count of status=new executions
> y (confirm - backup taken first)
> Queued executions cleared
```

### Download Logs Bundle
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 6 (Logs)
> 2 (Download log bundle)
> Check ~/Downloads for .tar.gz file
```

### Disable 2FA
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 5 (User & Access)
> 1 (Disable 2FA)
> user@example.com
> y (confirm)
> Run /cloudbot notify command in Slack
```

### Change Owner Email
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 5 (User & Access)
> 2 (Change owner)
> y (verification complete)
> new-owner@example.com
> CONFIRM
> Run /cloudbot redeploy-instance in Slack
```

### Export with Custom Backup Limit (v1.4.2)
```bash
cloudmedic
> 1 (Full medic operations)
> myworkspace
> 48
> 2 (Workflow Operations)
> 2 (Export from backup)
> 100 (show 100 backups instead of default 20)
> Select specific backup or press Enter for latest
> Check ~/Downloads for .zip file
```

## What's New

### v1.4.2 (Latest)
- **Configurable backup list** - Choose 20/50/100/all backups when viewing
- **Health Check** - Now a direct action from main menu
- **Storage Diagnostics** - Comprehensive disk, DB, and binary data analysis
- **Clear queued executions** - Remove status=new executions (with backup)
- **Prune binary data** - Clean old execution data via bfp-9000 sidecar
- **Reorganized menus** - 7 categorized submenus for better navigation

### v1.4
- **OOM Investigation** - Deep database analysis with report generation
  - Identifies execution data bloat, large workflows, error patterns
  - Generates downloadable Markdown reports
  - Provides actionable recommendations

### v1.3
- **Pre-menu** - Choose between live instance or deleted instance recovery
- **Deleted instance recovery** - Export workflows from backups (90-day retention)
- **Improved error handling** - Better messages when pod unavailable

### v1.2
- **Download logs** - n8n, backup, k8s events, execution logs, or bundle
- **Disable 2FA** - Remove 2FA for users
- **Change owner** - Update workspace owner email
- **Execution checker** - Status analysis with year 3000 detection

## Tips

### Backup List Limits
- **20 (default)** - Quick check for recent backups
- **50** - Good for finding backups from last ~2 months
- **100** - For older backups or detailed investigation
- **all** - Show everything (can be hundreds of entries)

### Storage Management
1. Run **Storage Diagnostics** (4→2) first to identify issues
2. If binary data is large, use **Prune Binary Data** (4→3)
3. For deep analysis, use **OOM Investigation** (4→1→9)

### Safety Features
- Backups taken before destructive operations
- Safety confirmations for critical actions
- CONFIRM required for owner email changes
- Color-coded warnings and status messages

## That's It!

The tool handles all the kubectl commands, cluster switching, and file management automatically.

Questions? Check the full README.
