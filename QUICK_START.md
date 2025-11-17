# Support Medic Tool - Quick Start

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

1. Enter workspace name (e.g., `guesty`)
2. Enter cluster (e.g., `prod-users-gwc-12`)
3. Tool finds pod automatically
4. Select operation from menu
5. Done!

## Most Common Operations

```
1  → Export workflows (saves to ~/Downloads)
2  → Export from backup (when instance is deleted)
4  → Deactivate all workflows (for crashloops)
6  → Check execution error
7  → Cancel pending executions
11 → Open database shell
```

## Examples

### Handle Crashloop
```bash
cloudmedic
> guesty
> prod-users-gwc-12
> 4 (deactivate all)
> y (confirm)
> Run /cloudbot redeploy-instance guesty in Slack
```

### Export for Customer
```bash
cloudmedic
> customername
> prod-users-gwc-48
> 1 (export from live)
> Check ~/Downloads for file
```

### Check Failed Execution
```bash
cloudmedic
> workspace
> cluster
> 6 (check execution)
> 225827 (execution ID)
> y (view error details)
```

## That's It!

The tool handles all the kubectl commands, cluster switching, and file management automatically.

Questions? Check the full README.
