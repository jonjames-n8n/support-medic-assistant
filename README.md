# Support Medic Assistant Tool

A Python CLI tool that streamlines n8n Support Medic operations with an interactive menu system.


## Features

- Interactive menu-driven interface with **7 categorized submenus** (v1.4.2)
- Auto-discovery of pod names
- Automatic downloads to ~/Downloads folder
- Safety confirmations for destructive operations
- Colour-coded output for better readability
- Database backup before modifications
- **v1.4.2:** Configurable backup list limit (20/50/100/all backups)
- **v1.4.2:** Health Check as direct action from main menu
- **v1.4.2:** Storage Diagnostics with disk, database, and binary data analysis
- **v1.4.2:** Clear queued executions (status=new)
- **v1.4.2:** Prune binary data via bfp-9000 sidecar
- **v1.4:** OOM Investigation with deep database analysis and report generation
- **v1.3:** Pre-menu for operation mode selection
- **v1.3:** Deleted instance recovery (list/export workflows from backups)
- **v1.3:** Improved error handling when pod not available
- **v1.2:** Execution status checker with year 3000 detection
- **v1.2:** Log download menu (n8n, backup, k8s, execution, bundle)
- **v1.2:** Disable 2FA for users
- **v1.2:** Change owner email

## 🖥️ Platform-Specific Versions

This tool is available in two versions optimized for different operating systems:

### 🐧 Linux/Mac Users
- **Use**: `support_medic_tool.py`
- **Installer**: `./install.sh`
- **Documentation**: This README

### 🪟 Windows Users
- **Use**: `support_medic_tool_windows.py`
- **Installer**: `.\install.ps1` (PowerShell)
- **Documentation**: [README_WINDOWS.md](README_WINDOWS.md) ← **Start here!**

**Both versions have identical features** - choose based on your operating system.

---

## Prerequisites (Linux/Mac)

- Python 3.6 or higher
- `kubectl` installed and configured
- `kubectx` installed
- Access to n8n Cloud clusters
- VPN connection active

## Installation (Linux/Mac)

> **Windows Users**: Use `install.ps1` instead - see [README_WINDOWS.md](README_WINDOWS.md)

### Quick Install (Recommended)

```bash
./install.sh
```

The installer will:
- Check for Python 3, kubectl, and kubectx
- Let you choose: global install, alias, or manual run
- Set up the `cloudmedic` command

### Option 1: Direct Run (No Installation)

```bash
python3 support_medic_tool.py
```

### Option 2: Make it Globally Accessible

```bash
# Make executable
chmod +x support_medic_tool.py

# Move to /usr/local/bin (or any directory in your PATH)
sudo cp support_medic_tool.py /usr/local/bin/cloudmedic

# Now run from anywhere:
cloudmedic
```

### Option 3: Create an Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias cloudmedic="python3 /path/to/support_medic_tool.py"
```

Then run:
```bash
source ~/.zshrc  # or ~/.bashrc
cloudmedic
```

## Usage

### 1. Launch the Tool

```bash
python3 support_medic_tool.py
# or
cloudmedic  # if installed globally
```

### 2. Select Operation Mode (v1.3)

You'll first see a pre-menu to choose your operation mode:

**Option 1: Full medic operations (live instance)**
- For live instances with active pods
- Requires workspace name and cluster number
- Full access to all medic operations

**Option 2: Recover workflows from deleted instance**
- For deleted instances (backups only)
- Only requires instance name
- Access to backup listing and workflow export

### 3. Enter Required Details

**For Live Instances (Option 1):**
- **Workspace name** (e.g., `myworkspace`)
- **Cluster number** (e.g., `48` for prod-users-gwc-48)

The tool will automatically:
- Switch to the specified cluster
- Find the pod for that workspace
- Display the main menu

**For Deleted Instances (Option 2):**
- **Instance name** (e.g., `deleted-workspace`)
- No cluster needed (uses services-gwc-1 for backups)
- Displays deleted instance recovery menu

### 4. Select an Operation

**v1.4.2 Menu Structure:** The main menu now has 7 categorized submenus for better organization:

```
╔══════════════════════════════════════════════════════════════╗
║              SUPPORT MEDIC ASSISTANT v1.4.2                   ║
╚══════════════════════════════════════════════════════════════╝

Workspace: example-user | Cluster: prod-users-gwc-3

1. Health Check                  ← Direct action (runs immediately)
2. Workflow Operations
3. Execution Management
4. Database & Storage
5. User & Access
6. Logs
7. Settings

q. Quit
```

#### **1. Health Check** (Direct Action)
Runs immediately - no submenu. Shows:
- Pod status, container readiness, restart count
- Database size and connection status
- Recent errors and execution counts

#### **2. Workflow Operations**
- Export workflows (live instance) - Saves to Downloads as `.json.gz`
- Export workflows (from backup) - **v1.4.2: Choose 20/50/100/all backups**
- Import workflows
- Deactivate all workflows
- Deactivate specific workflow

#### **3. Execution Management**
- Check execution by ID
- Cancel pending executions (status=pending)
- Cancel waiting executions (status=waiting)
- **v1.4.2: Clear queued executions** (status=new) - Takes backup first

#### **4. Database & Storage**
- Database troubleshooting (guided) - **Includes OOM Investigation (v1.4)**
- **v1.4.2: Storage diagnostics** - Disk, database, execution counts, binary data analysis
- **v1.4.2: Prune binary data** - Via bfp-9000 sidecar
- Take backup

#### **5. User & Access**
- Disable 2FA
- Change owner email

#### **6. Logs**
- View recent logs
- Download log bundle

#### **7. Settings**
- Change workspace/cluster
- Redeploy instance

#### **Pre-Menu: Deleted Instance Recovery** (v1.3)
- List available backups - **v1.4.2: Choose 20/50/100/all**
- Export workflows (latest backup)
- Export workflows (select backup) - **v1.4.2: Choose 20/50/100/all**
- Back to start

## Examples

### Example 1: Recover Workflows from Deleted Instance (v1.3)

```
$ cloudmedic

╔══════════════════════════════════════════════════════════════╗
║              SUPPORT MEDIC ASSISTANT v1.4.2                   ║
╚══════════════════════════════════════════════════════════════╝

Select operation mode:

1. Full medic operations (live instance)
2. Recover workflows from deleted instance

q. Quit

Select option: 2

==============================================================
      Deleted Instance Recovery - Setup
==============================================================

⚠ REMINDER: Make sure you're connected to the VPN!

Enter instance name: deleted-workspace

==============================================================
           Deleted Instance Recovery
==============================================================
Instance: deleted-workspace

1. List available backups
2. Export workflows (latest backup)
3. Export workflows (select backup)
4. Back to start

Select option: 2

ℹ Connecting to backup service...
ℹ Exporting workflows from latest backup...
ℹ Downloading workflows...
✓ Workflows exported to: /Users/you/Downloads/deleted-workspace-workflows-backup-20251113.zip
ℹ File size: 245.3 KB
```

### Example 2: Export Workflows for Customer

```
$ cloudmedic

Enter workspace name: myworkspace
Enter cluster number: 48
ℹ Switching to cluster prod-users-gwc-48...
✓ Switched to cluster: prod-users-gwc-48
ℹ Finding pod for workspace: myworkspace...
✓ Found pod: myworkspace-n8n-6856cbbf6d-xk2wq

╔══════════════════════════════════════════════════════════════╗
║              SUPPORT MEDIC ASSISTANT v1.4.2                   ║
╚══════════════════════════════════════════════════════════════╝

Workspace: myworkspace | Cluster: prod-users-gwc-48
Pod: myworkspace-n8n-6856cbbf6d-xk2wq

1. Health Check
2. Workflow Operations
3. Execution Management
4. Database & Storage
5. User & Access
6. Logs
7. Settings

q. Quit

Select an option: 2

Workflow Operations
1. Export workflows (live instance)
2. Export workflows (from backup)
3. Import workflows
4. Deactivate all workflows
5. Deactivate specific workflow

b. Back to main menu

Select an option: 1

ℹ Exporting workflows...
✓ Workflows exported to: /Users/you/Downloads/myworkspace-workflows-2025-11-21.json.gz
ℹ Extract with: gzip -d myworkspace-workflows-2025-11-21.json.gz
```

### Example 3: Handle Crashloop (Deactivate Workflows)

```
Select an option: 4

⚠ This will deactivate ALL active workflows!
Are you sure? (y/n): y

ℹ Taking backup first...
ℹ Deactivating workflows...
✓ All workflows deactivated
⚠ Redeploy instance for changes to take effect
```

### Example 4: Investigate Failed Execution

```
Select an option: 6

Enter execution ID: 1234

ℹ Fetching execution details...

Execution Summary:
1234|abc123def|1|webhook|2025-10-31 20:46:53.736|2025-10-31 20:47:43.859|error

View execution data (error details)? (y/n): y

[Shows full error JSON with details]
```

### Example 5: Download Logs Bundle (v1.2)

```
Select an option: 14

Log Download Menu
1. n8n container logs
2. backup-cron logs
3. Kubernetes events
4. Execution logs (by ID)
5. All logs (bundle)
6. Back to main menu

Select option: 5

ℹ Creating log bundle...
ℹ   • n8n container logs...
ℹ   • backup-cron logs...
ℹ   • Kubernetes events...
ℹ   • Pod description...
ℹ   • Execution summary...
ℹ   • Creating archive...
✓ Bundle created: myworkspace-logs-bundle-2025-11-21-143022.tar.gz (45.2 KB)
ℹ Location: /Users/you/Downloads/myworkspace-logs-bundle-2025-11-21-143022.tar.gz
```

### Example 6: Disable 2FA (v1.2)

```
Select an option: 15

Enter user email: user@example.com

ℹ Checking if user exists...

⚠ Warning: This will disable 2FA for:
  Email: user@example.com

Proceed with disabling 2FA? (y/n): y

ℹ Disabling 2FA...
✓ 2FA disabled for: user@example.com

Next step:
Run this command in Slack to notify the user:
  /cloudbot notify [user_id] disable-2fa [thread_id]
```

### Example 7: Change Owner Email (v1.2)

```
Select an option: 16

IMPORTANT CHECKS (you must verify):
  □ Verified identity via ownership verification KB
  □ Checked mission control - new email doesn't own another instance
  □ 2FA not enabled (or disabled first)

Have you completed all verification checks? (y/n): y

ℹ Fetching current owner...

Current owner: old-owner@example.com

Enter new owner email: new-owner@example.com

ℹ Checking if new email exists in workspace...

Confirm owner email change:
  Old: old-owner@example.com
  New: new-owner@example.com

Type 'CONFIRM' to proceed: CONFIRM

ℹ Taking backup first...
ℹ Updating owner email...
ℹ Verifying change...
✓ Owner email updated successfully!

Important notes:
  • New owner must use 'Forgot Password' to set password
  • Redeploy instance for changes to take effect

Next step:
Run this command in Slack:
  /cloudbot redeploy-instance myworkspace
```

### Example 8: OOM Investigation with Report Generation (v1.4)

```
Select an option: 11

==============================================================
           Database Troubleshooting Menu
==============================================================

1. View active workflows count
2. View total executions count
3. Check for workflows with errors
4. Find workflows by name
5. Show workflow details
6. Show execution details
7. List tables in database
8. Execution status checker
9. Investigate OOM cause
10. Raw SQL shell (advanced)
11. Back to main menu

Select option: 9

╔══════════════════════════════════════════════════════════════╗
║                    OOM INVESTIGATION                         ║
╚══════════════════════════════════════════════════════════════╝

Analyzing database for OOM causes...

──────────────────────────────────────────────────
 DATABASE OVERVIEW
──────────────────────────────────────────────────

Database Size: 342.5 MB
Total Executions: 45,234
Active Workflows: 12
Inactive Workflows: 8

──────────────────────────────────────────────────
 TABLE SIZES
──────────────────────────────────────────────────

execution_data           187.3 MB  ⚠ Potential bloat!
execution_entity          98.6 MB
workflow_entity            2.1 MB
settings                   1.2 MB
credentials_entity         0.8 MB
(showing top 5 tables)

──────────────────────────────────────────────────
 LARGEST EXECUTIONS
──────────────────────────────────────────────────

Execution ID  Workflow ID  Workflow Name              Data Size  Status
12345         wf789       "Data Processing Pipeline"   15.2 MB   success
12340         wf789       "Data Processing Pipeline"   14.8 MB   success
12298         wf456       "API Integration Job"        12.3 MB   error
12250         wf789       "Data Processing Pipeline"   11.9 MB   success
12189         wf456       "API Integration Job"        10.7 MB   success

──────────────────────────────────────────────────
 WORKFLOWS WITH MOST STORED DATA
──────────────────────────────────────────────────

Workflow ID  Name                         Active  Total Data  Exec Count
wf789       "Data Processing Pipeline"    Yes     156.8 MB    3,245
wf456       "API Integration Job"         No       87.3 MB    1,892
wf123       "Email Notifications"         Yes      12.4 MB      876
wf321       "Webhook Handler"             Yes       8.2 MB    2,156
wf654       "Scheduled Reports"           No        6.1 MB      234

⚠ Found 87.3 MB of data in INACTIVE workflows!

──────────────────────────────────────────────────
 TOP WORKFLOWS BY EXECUTIONS (Last 24h)
──────────────────────────────────────────────────

Workflow ID  Name                      Execution Count
wf321       "Webhook Handler"                   234
wf789       "Data Processing Pipeline"          145
wf123       "Email Notifications"                89
wf901       "Slack Bot"                          67
wf234       "CRM Sync"                           45

──────────────────────────────────────────────────
 WORKFLOWS WITH ERRORS (Last 24h)
──────────────────────────────────────────────────

Workflow ID  Name                    Error Count  Sample Error
wf456       "API Integration Job"           23    "Request timeout after 60s"
wf789       "Data Processing"                8    "Cannot read property 'data'"
wf234       "CRM Sync"                       3    "Invalid API credentials"

──────────────────────────────────────────────────
 EXECUTION QUEUE STATUS
──────────────────────────────────────────────────

Pending: 12
Waiting: 5
Running: 3

──────────────────────────────────────────────────
 EXECUTION GROWTH TREND (Last 7 Days)
──────────────────────────────────────────────────

Date        New Executions
2025-11-28        892
2025-11-27        856
2025-11-26        923
2025-11-25        801
2025-11-24        767
2025-11-23        834
2025-11-22        798

═══════════════════════════════════════════════════
 LIKELY CULPRITS IDENTIFIED
═══════════════════════════════════════════════════

⚠ EXECUTION DATA TABLE BLOAT
  • execution_data table is 187.3 MB (threshold: 100 MB)
  • This table stores execution results and can grow rapidly
  • Recommendation: Review execution retention settings

⚠ INACTIVE WORKFLOW DATA
  • Found 87.3 MB of data in inactive workflows (threshold: 10 MB)
  • Workflows: "API Integration Job" (87.3 MB)
  • Recommendation: Consider purging old execution data for inactive workflows

⚠ LARGE INDIVIDUAL EXECUTIONS
  • Found 5 executions larger than 10 MB each
  • Workflow "Data Processing Pipeline" has multiple large executions
  • Recommendation: Optimize data handling in this workflow

⚠ LARGE DATABASE SIZE
  • Database is 342.5 MB (threshold: 200 MB)
  • Recommendation: Consider implementing data retention policies

═══════════════════════════════════════════════════
 RECOMMENDED ACTIONS
═══════════════════════════════════════════════════

1. IMMEDIATE ACTIONS:
   • Deactivate error-prone workflows temporarily
   • Clear pending/waiting execution queue
   • Export workflows before making changes

2. DATA CLEANUP:
   • Delete old execution data for inactive workflows
   • Prune execution_data for completed executions older than 30 days
   • Consider vacuum/optimize database after cleanup

3. PREVENTION:
   • Set execution retention to 30 days or less
   • Optimize "Data Processing Pipeline" to reduce data storage
   • Monitor execution_data table size weekly

Generate detailed report? (y/n): y

ℹ Generating comprehensive OOM investigation report...
✓ Report saved to: /Users/you/Downloads/example-workspace-oom-report-20251128-143022.md
ℹ Report size: 12.4 KB

The report includes:
  • All findings and metrics
  • SQL commands for data cleanup
  • kubectl commands for investigation
  • Customer-facing recommendations

Press Enter to continue...
```

## Feature Guide: OOM Investigation

The OOM Investigation feature (v1.4) helps identify and resolve Out of Memory issues by analyzing database metrics and execution patterns.

### When to Use

Use OOM Investigation when:
- Instance is crashlooping or running out of memory
- Database size is growing unexpectedly
- Customer reports slow performance or failures
- You need to identify data bloat sources

### How to Use

1. **Access the feature**: Main Menu → Database Troubleshooting (11) → Investigate OOM cause (9)

2. **Review the analysis**: The tool will automatically analyze:
   - Database and table sizes
   - Largest executions by data size
   - Workflows with most stored data
   - Execution trends and queue status
   - Error-prone workflows

3. **Check "Likely Culprits"**: The tool identifies issues with intelligent thresholds:
   - Table bloat (execution_data > 100 MB)
   - Inactive workflow data (> 10 MB)
   - Large individual executions (> 10 MB each)
   - Pending backlog (> 100 pending)
   - Overall database size (> 200 MB)

4. **Generate report**: Create a downloadable Markdown report with:
   - Complete findings summary
   - SQL commands for cleanup
   - kubectl commands for investigation
   - Customer-friendly recommendations

### Interpreting Results

**🟢 Green flags:**
- Database < 200 MB
- execution_data table < 100 MB
- No large inactive workflows
- Steady execution growth

**🟡 Yellow flags:**
- Database 200-500 MB
- Some large executions (5-10 MB)
- Minor error rates in workflows
- Growing pending queue

**🔴 Red flags:**
- Database > 500 MB
- execution_data table > 200 MB
- Large inactive workflows (> 50 MB)
- Many executions > 10 MB
- High error rates in active workflows

### Common Scenarios

**Scenario 1: Execution Data Bloat**
- **Symptom**: execution_data table > 100 MB
- **Cause**: Long retention period or workflows storing large data
- **Solution**: Reduce retention period, optimize workflows

**Scenario 2: Inactive Workflow Data**
- **Symptom**: Large data in deactivated workflows
- **Cause**: Old workflows still storing execution history
- **Solution**: Purge execution data for inactive workflows

**Scenario 3: Individual Large Executions**
- **Symptom**: Single executions > 10 MB
- **Cause**: Workflow processing large datasets inefficiently
- **Solution**: Optimize workflow data handling, use pagination

**Scenario 4: Crashloop from Pending Queue**
- **Symptom**: Many pending executions (> 100)
- **Cause**: Workflows triggering faster than they can execute
- **Solution**: Cancel pending queue, fix trigger logic

### Example 9: Storage Diagnostics (v1.4.2)

```
Main Menu → 4. Database & Storage → 2. Storage diagnostics

╔══════════════════════════════════════════════════════════════╗
║                  STORAGE DIAGNOSTICS                          ║
╚══════════════════════════════════════════════════════════════╝

Analyzing storage usage...

──────────────────────────────────────────────────
 1. DISK USAGE
──────────────────────────────────────────────────
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       100G   45G   55G  45% /data

──────────────────────────────────────────────────
 2. DATABASE SIZE
──────────────────────────────────────────────────
Database: 561M database.sqlite

Table Breakdown:
  execution_data: 412.3 MB
  execution_entity: 89.5 MB
  workflow_entity: 15.2 MB

──────────────────────────────────────────────────
 3. EXECUTION COUNTS
──────────────────────────────────────────────────
Total Executions: 125,432

By Status:
  success: 98,234
  error: 15,678
  waiting: 234

Last 7 Days:
  2025-12-03: 1,234 executions
  2025-12-02: 2,345 executions
  2025-12-01: 1,567 executions

──────────────────────────────────────────────────
 4. BINARY DATA
──────────────────────────────────────────────────
Binary Data Entries: 45,678
Total Size: 156.7 MB

⚠ Binary data is 156.7 MB - consider pruning

Top Workflows by Stored Data:
  1. Data Processing Flow (xyz123): 78.4 MB [ACTIVE]
  2. Webhook Handler (abc456): 45.2 MB [inactive]
  3. Daily Sync (def789): 23.1 MB [ACTIVE]

──────────────────────────────────────────────────
 5. RECOMMENDATIONS
──────────────────────────────────────────────────
• Run 'Prune binary data' to clean old execution data
• Inactive workflows have significant stored data - consider cleanup
✓ Disk usage is healthy (45%)
```

### Example 10: Configurable Backup List (v1.4.2)

```
Main Menu → 2. Workflow Operations → 2. Export workflows (from backup)

╔══════════════════════════════════════════════════════════════╗
║              Export Workflows (From Backup)                   ║
╚══════════════════════════════════════════════════════════════╝

ℹ Switching to services-gwc-1...

How many backups to display? [20/50/100/all]
Enter choice (default 20): 100

ℹ Listing available backups...

Available backups:
myworkspace_sqldump_20251203_0315.tar
myworkspace_sqldump_20251202_0315.tar
myworkspace_sqldump_20251201_0315.tar
...
[100 backups shown]

Enter backup name (or press Enter for latest): myworkspace_sqldump_20251115_0315.tar

ℹ Exporting workflows...
✓ Workflows downloaded to: ~/Downloads/myworkspace-workflows-backup-20251115.zip
ℹ File size: 287.5 KB
```

**Use Cases:**
- Finding older backups beyond the default 20
- Recovering workflows from a specific date
- Investigating when a workflow was deleted

### Best Practices

1. **Always export workflows first** before making any changes
2. **Generate and save the report** for documentation
3. **Share findings with customer** using the customer-facing recommendations
4. **Monitor after cleanup** to ensure the issue is resolved
5. **Set retention policies** to prevent future bloat

## File Locations

- **Exported workflows:** `~/Downloads/<workspace>-workflows-<date>.json.gz`
- **Backup exports:** `~/Downloads/<workspace>-workflows-backup-<date>.zip`
- **Log downloads:** `~/Downloads/<workspace>-<logtype>-<timestamp>.txt`
- **Log bundles:** `~/Downloads/<workspace>-logs-bundle-<timestamp>.tar.gz`
- **OOM reports:** `~/Downloads/<workspace>-oom-report-<timestamp>.md` (v1.4)
- **Tool location:** Wherever you placed `support_medic_tool.py`

## Tips

### Quick Access Setup

For fastest access, I recommend:

```bash
# 1. Make executable
chmod +x support_medic_tool.py

# 2. Move to bin
sudo cp support_medic_tool.py /usr/local/bin/cloudmedic

# 3. Create short alias
echo 'alias cm="cloudmedic"' >> ~/.zshrc
source ~/.zshrc

# Now run with just:
cm
```

### Working with Multiple Workspaces

You can change workspace without restarting:
- Select option `13` to enter new workspace/cluster
- Or quit and restart the tool

### Safety Features

The tool includes safety measures:
- Confirms destructive operations
- Takes backup before deactivating workflows
- Shows counts before bulk operations
- Displays current workspace context
- Requires CONFIRM to change owner email

### Database Shell Tips

When using option `11` (Database troubleshooting) → option `9` (Raw SQL shell):
```sql
-- Common queries
SELECT id, name, active FROM workflow_entity;
SELECT status, COUNT(*) FROM execution_entity GROUP BY status;
.tables          -- List all tables
.schema <table>  -- Show table structure
.quit            -- Exit shell
```

### Execution Status Checker (v1.2)

Access via Database Troubleshooting → Option 8:
- **Waiting executions** - Detects "year 3000" stuck executions
- **Pending executions** - Warns about crashloop risk (>100 pending)
- **Running executions** - Shows long-running executions
- **Error analysis** - Groups errors by workflow
- **All statuses summary** - Color-coded overview

## Troubleshooting

### "Command not found: kubectx"

Install kubectx:
```bash
brew install kubectx  # macOS
```

### "Could not find pod"

Verify:
- Workspace name is correct
- You're connected to VPN
- Cluster exists and you have access

### "Permission denied"

Make the script executable:
```bash
chmod +x support_medic_tool.py
```

### Downloads not working

The tool saves to `~/Downloads` by default. If you want a different location, edit line 46 in the script:
```python
self.downloads_dir = Path.home() / "Downloads"  # Change this
```

## Advanced: Customization

### Change Download Directory

Edit line 46:
```python
self.downloads_dir = Path("/path/to/your/folder")
```

### Add Custom Operations

Add your own menu option in the `show_main_menu()` method:
```python
("17", "My custom operation", self.my_custom_function),
```

Then create the function:
```python
def my_custom_function(self):
    self.print_header("My Custom Operation")
    # Your code here
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
```

## Support

For issues or feature requests:
- GitHub Issues: https://github.com/jonjames-n8n/support-medic-assistant/issues
- Internal Support: Jon James

## Version

Current version: 1.4
Last updated: November 2025

### What's New in v1.4

- **OOM Investigation with Report Generation** - Comprehensive database analysis tool
  - **Deep Database Analysis**: Database size, table sizes, execution data bloat detection
  - **Intelligent Root Cause Identification**: Automatic detection of likely OOM culprits
  - **Workflow Analysis**: Find workflows with most stored data (active vs inactive)
  - **Execution Trends**: View execution growth over last 7 days
  - **Error Analysis**: Identify workflows with recent errors
  - **Downloadable Reports**: Generate detailed Markdown reports with:
    - Database metrics and findings
    - Actionable recommendations
    - SQL commands for data cleanup
    - Customer-facing explanations
  - Access via: Database Troubleshooting (Option 11) → Investigate OOM cause (Option 9)

### What's New in v1.3

- **Pre-menu for Operation Mode**: Choose between full medic operations or deleted instance recovery at startup
- **Deleted Instance Recovery**: Recover workflows from deleted instances using backups
  - List available backups (retained for 90 days)
  - Export workflows from latest backup
  - Export workflows from specific backup
- **Improved Error Handling**: Better handling when pod is not available
  - Clear error messages when attempting pod-required operations
  - Suggestions for available operations without pod
- **Enhanced Export Validation**: Export operations now properly validate success/failure
