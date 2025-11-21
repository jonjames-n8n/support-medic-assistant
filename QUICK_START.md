# Support Medic Tool - Quick Start (v1.2)

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

1. Enter workspace name (e.g., `myworkspace`)
2. Enter cluster number (e.g., `48` for prod-users-gwc-48)
3. Tool finds pod automatically
4. Select operation from menu
5. Done!

## Most Common Operations

```
0  → Health check (quick status overview)
1  → Export workflows (saves to ~/Downloads)
2  → Export from backup (when instance is deleted)
4  → Deactivate all workflows (for crashloops)
6  → Check execution error
7  → Cancel pending executions
11 → Database troubleshooting (guided)
14 → Download logs (NEW in v1.2)
15 → Disable 2FA (NEW in v1.2)
16 → Change owner email (NEW in v1.2)
```

## Examples

### Handle Crashloop
```bash
cloudmedic
> myworkspace
> 48
> 4 (deactivate all)
> y (confirm)
> Run /cloudbot redeploy-instance myworkspace in Slack
```

### Export for Customer
```bash
cloudmedic
> customer-workspace
> 52
> 1 (export from live)
> Check ~/Downloads for file
```

### Check Failed Execution
```bash
cloudmedic
> myworkspace
> 48
> 6 (check execution)
> 1234 (execution ID)
> y (view error details)
```

### Download Logs Bundle (v1.2)
```bash
cloudmedic
> myworkspace
> 48
> 14 (download logs)
> 5 (all logs bundle)
> Check ~/Downloads for .tar.gz file
```

### Disable 2FA (v1.2)
```bash
cloudmedic
> myworkspace
> 48
> 15 (disable 2FA)
> user@example.com
> y (confirm)
> Run /cloudbot notify command in Slack
```

### Change Owner Email (v1.2)
```bash
cloudmedic
> myworkspace
> 48
> 16 (change owner)
> y (verification complete)
> new-owner@example.com
> CONFIRM
> Run /cloudbot redeploy-instance in Slack
```

### Check Stuck Executions (v1.2)
```bash
cloudmedic
> myworkspace
> 48
> 11 (database troubleshooting)
> 8 (check executions by status)
> 1 (waiting executions - detects "year 3000" stuck)
```

## v1.2 New Features

| Option | Feature | Description |
|--------|---------|-------------|
| 14 | Download Logs | n8n, backup, k8s events, execution logs, or bundle |
| 15 | Disable 2FA | Disable multi-factor auth for users |
| 16 | Change Owner | Update workspace owner email |
| 11→8 | Execution Checker | Detailed status analysis with year 3000 detection |

## That's It!

The tool handles all the kubectl commands, cluster switching, and file management automatically.

Questions? Check the full README.
