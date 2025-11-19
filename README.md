# Support Medic Assistant Tool

A Python CLI tool that streamlines n8n Support Medic operations with an interactive menu system.

## Features

- Interactive menu-driven interface
- Auto-discovery of pod names
- Automatic downloads to ~/Downloads folder
- Safety confirmations for destructive operations
- Colour-coded output for better readability
- Database backup before modifications

## Prerequisites

- Python 3.6 or higher
- `kubectl` installed and configured
- `kubectx` installed
- Access to n8n Cloud clusters
- VPN connection active

## Installation

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
- **Workspace name** (e.g., `jonwjames`)
- **Cluster** (e.g., `prod-users-gwc-48`) -- only cluster number is required as of version 1.1

The tool will automatically:
- Switch to the specified cluster
- Find the pod for that workspace
- Display the main menu

### 3. Select an Operation

Available operations:

**Health Check:**
- `0` - Provides a quick glance status of Pod Health, DB Size, Number of Restarts etc

**Workflow Management:**
- `1` - Export workflows (from live instance) → Saves to Downloads as `.json.gz`
- `2` - Export workflows (from backup) → Lists backups, lets you choose, saves as `.zip`
- `3` - Import workflows → Shows files in Downloads, imports selected file
- `4` - Deactivate all workflows → Confirms, takes backup, deactivates all
- `5` - Deactivate specific workflow → Enter workflow ID to deactivate

**Execution Management:**
- `6` - Check execution by ID → Shows execution summary and error details
- `7` - Cancel pending executions → Counts, confirms, cancels all pending
- `8` - Cancel waiting executions → Counts, confirms, cancels all waiting

**Maintenance:**
- `9` - Take backup → Creates manual backup
- `10` - View recent logs → Shows last N lines of n8n logs
- `11` - Open database shell → Interactive SQLite shell (type `.quit` to exit)
- `12` - Redeploy instance → Shows cloudbot command to run in Slack

**Navigation:**
- `13` - Change workspace/cluster → Start over with different workspace
- `q` - Quit

## Examples

### Example 1: Export Workflows for Customer

```
$ cloudmedic

Enter workspace name: myn8nworkspace
Enter cluster: prod-users-gwc-12
ℹ Switching to cluster prod-users-gwc-12...
✓ Switched to cluster: prod-users-gwc-12
ℹ Finding pod for workspace: myn8nworkspace...
✓ Found pod: myn8nworkspace-n8n-6856cbbf6d-xk2wq

Main Menu
Workspace: myn8nworkspace
Cluster: prod-users-gwc-12
Pod: myn8nworkspace-n8n-6856cbbf6d-xk2wq

1. Export workflows (from live instance)
2. Export workflows (from backup)
...

Select an option: 1

ℹ Exporting workflows...
✓ Workflows exported to: /Users/jon/Downloads/myn8nworkspace-workflows-2025-11-17.json.gz
ℹ Extract with: gzip -d myn8nworkspace-workflows-2025-11-17.json.gz
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

Enter execution ID: 225827

ℹ Fetching execution details...

Execution Summary:
225827|4zDDf5yIkyfP47OR|1|webhook|2025-10-31 20:46:53.736|2025-10-31 20:47:43.859|error

View execution data (error details)? (y/n): y

[Shows full error JSON with details]
```

## File Locations

- **Exported workflows:** `~/Downloads/<workspace>-workflows-<date>.json.gz`
- **Backup exports:** `~/Downloads/<workspace>-workflows-backup-<date>.zip`
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

### Database Shell Tips

When using option `11` (Database shell):
```sql
-- Common queries
SELECT id, name, active FROM workflow_entity;
SELECT status, COUNT(*) FROM execution_entity GROUP BY status;
.tables          -- List all tables
.schema <table>  -- Show table structure
.quit            -- Exit shell
```

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

The tool saves to `~/Downloads` by default. If you want a different location, edit line 15 in the script:
```python
self.downloads_dir = Path.home() / "Downloads"  # Change this
```

## Advanced: Customization

### Change Download Directory

Edit line 15:
```python
self.downloads_dir = Path("/path/to/your/folder")
```

### Add Custom Operations

Add your own menu option in the `show_main_menu()` method:
```python
("14", "My custom operation", self.my_custom_function),
```

Then create the function:
```python
def my_custom_function(self):
    self.print_header("My Custom Operation")
    # Your code here
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
```

## Support

For issues or feature requests, contact Jon James

## Version

Current version: 1.0
Last updated: November 2025

---

**Happy Medic-ing!** 🚀
