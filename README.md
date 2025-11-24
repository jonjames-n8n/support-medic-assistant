# Support Medic Assistant Tool

A Python CLI tool that streamlines n8n Support Medic operations with an interactive menu system.

## Privacy & Security Notice

**IMPORTANT:** Never share real customer data in public documentation or screenshots.

All examples in this documentation use generic placeholder names:
- Workspaces: `myworkspace`, `customer-workspace`
- Workflows: `Data Sync`, `Customer Onboarding`
- Emails: `user@example.com`

When creating support tickets or documentation:
- Use generic examples
- Never include real customer workspace names
- Never include real workflow names
- Never include real execution data

## Features

- Interactive menu-driven interface
- Auto-discovery of pod names
- Automatic downloads to ~/Downloads folder
- Safety confirmations for destructive operations
- Colour-coded output for better readability
- Database backup before modifications
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

### 2. Enter Workspace Details

You'll be prompted for:
- **Workspace name** (e.g., `myworkspace`)
- **Cluster number** (e.g., `48` for prod-users-gwc-48)

The tool will automatically:
- Switch to the specified cluster
- Find the pod for that workspace
- Display the main menu

### 3. Select an Operation

Available operations:

**Health Check:**
- `0` - Provides a quick glance status of Pod Health, DB Size, Number of Restarts etc

**Workflow Management:**
- `1` - Export workflows (from live instance) - Saves to Downloads as `.json.gz`
- `2` - Export workflows (from backup) - Lists backups, lets you choose, saves as `.zip`
- `3` - Import workflows - Shows files in Downloads, imports selected file
- `4` - Deactivate all workflows - Confirms, takes backup, deactivates all
- `5` - Deactivate specific workflow - Enter workflow ID to deactivate

**Execution Management:**
- `6` - Check execution by ID - Shows execution summary and error details
- `7` - Cancel pending executions - Counts, confirms, cancels all pending
- `8` - Cancel waiting executions - Counts, confirms, cancels all waiting

**Maintenance:**
- `9` - Take backup - Creates manual backup
- `10` - View recent logs - Shows last N lines of n8n logs
- `11` - Database troubleshooting (guided) - Pre-built queries for common issues
- `12` - Redeploy instance - Shows cloudbot command to run in Slack

**v1.2 New Features:**
- `14` - Download logs - Download n8n, backup, k8s events, or execution logs
- `15` - Disable 2FA - Disable multi-factor authentication for a user
- `16` - Change owner email - Update workspace owner email address

**Navigation:**
- `13` - Change workspace/cluster - Start over with different workspace
- `q` - Quit

## Examples

### Example 1: Export Workflows for Customer

```
$ cloudmedic

Enter workspace name: myworkspace
Enter cluster number: 48
ℹ Switching to cluster prod-users-gwc-48...
✓ Switched to cluster: prod-users-gwc-48
ℹ Finding pod for workspace: myworkspace...
✓ Found pod: myworkspace-n8n-6856cbbf6d-xk2wq

Main Menu
Workspace: myworkspace
Cluster: prod-users-gwc-48
Pod: myworkspace-n8n-6856cbbf6d-xk2wq

1. Export workflows (from live instance)
2. Export workflows (from backup)
...

Select an option: 1

ℹ Exporting workflows...
✓ Workflows exported to: /Users/you/Downloads/myworkspace-workflows-2025-11-21.json.gz
ℹ Extract with: gzip -d myworkspace-workflows-2025-11-21.json.gz
```

### Example 2: Handle Crashloop (Deactivate Workflows)

```
Select an option: 4

⚠ This will deactivate ALL active workflows!
Are you sure? (y/n): y

ℹ Taking backup first...
ℹ Deactivating workflows...
✓ All workflows deactivated
⚠ Redeploy instance for changes to take effect
```

### Example 3: Investigate Failed Execution

```
Select an option: 6

Enter execution ID: 1234

ℹ Fetching execution details...

Execution Summary:
1234|abc123def|1|webhook|2025-10-31 20:46:53.736|2025-10-31 20:47:43.859|error

View execution data (error details)? (y/n): y

[Shows full error JSON with details]
```

### Example 4: Download Logs Bundle (v1.2)

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

### Example 5: Disable 2FA (v1.2)

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

### Example 6: Change Owner Email (v1.2)

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

## File Locations

- **Exported workflows:** `~/Downloads/<workspace>-workflows-<date>.json.gz`
- **Backup exports:** `~/Downloads/<workspace>-workflows-backup-<date>.zip`
- **Log downloads:** `~/Downloads/<workspace>-<logtype>-<timestamp>.txt`
- **Log bundles:** `~/Downloads/<workspace>-logs-bundle-<timestamp>.tar.gz`
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
- Internal Support: #cloud-support

## Version

Current version: 1.2
Last updated: November 2025
