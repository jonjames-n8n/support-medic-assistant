# Cloud Medic Tool - Windows Installation Script
# Requires PowerShell 5.0 or later

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Cloud Medic Tool - Windows Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion.Major
if ($psVersion -lt 5) {
    Write-Host "❌ PowerShell 5.0 or later is required. You have version $psVersion" -ForegroundColor Red
    exit 1
}

# Check for Python 3
Write-Host "Checking dependencies..." -ForegroundColor Yellow
Write-Host ""

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "✓ Python 3 found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 3 is not installed or not in PATH" -ForegroundColor Red
        Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Python 3 is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check for pip and colorama
Write-Host "Checking for required Python packages..." -ForegroundColor Yellow
try {
    $pipList = pip list 2>&1 | Out-String
    if ($pipList -match "colorama") {
        Write-Host "✓ colorama package found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  colorama package not found" -ForegroundColor Yellow
        $installColorama = Read-Host "Install colorama? (Required for colored output) (y/n)"
        if ($installColorama -match "^[Yy]$") {
            Write-Host "Installing colorama..." -ForegroundColor Yellow
            pip install colorama
            Write-Host "✓ colorama installed" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Tool will work but without colored output" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "⚠️  Could not check for colorama package" -ForegroundColor Yellow
}

Write-Host ""

# Check for kubectl
try {
    $kubectlVersion = kubectl version --client --short 2>&1
    Write-Host "✓ kubectl found" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Install from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/" -ForegroundColor Yellow
    exit 1
}

# Check for kubectx
try {
    $kubectxVersion = kubectx --version 2>&1
    Write-Host "✓ kubectx found" -ForegroundColor Green
} catch {
    Write-Host "⚠️  kubectx not found" -ForegroundColor Yellow
    Write-Host "   Install from: https://github.com/ahmetb/kubectx" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -notmatch "^[Yy]$") {
        exit 1
    }
}

Write-Host ""

# Get script location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolPath = Join-Path $scriptDir "support_medic_tool_windows.py"

if (-not (Test-Path $toolPath)) {
    Write-Host "❌ support_medic_tool_windows.py not found in current directory" -ForegroundColor Red
    Write-Host "   Looking in: $scriptDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Tool file found: $toolPath" -ForegroundColor Green
Write-Host ""

# Installation options
Write-Host "Installation options:" -ForegroundColor Cyan
Write-Host "1. Create batch file in system PATH (recommended)" -ForegroundColor White
Write-Host "2. Add tool directory to PATH (requires admin/restart)" -ForegroundColor White
Write-Host "3. Create desktop shortcut only" -ForegroundColor White
Write-Host "4. Skip - run manually with 'python support_medic_tool_windows.py'" -ForegroundColor White
Write-Host ""

$option = Read-Host "Choose option (1/2/3/4)"

switch ($option) {
    "1" {
        # Create batch file in user's local bin directory
        Write-Host ""
        Write-Host "Creating batch file wrapper..." -ForegroundColor Yellow

        # Use user's local AppData for batch file
        $localBin = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

        if (-not (Test-Path $localBin)) {
            Write-Host "❌ WindowsApps directory not found: $localBin" -ForegroundColor Red
            Write-Host "   Trying alternative location..." -ForegroundColor Yellow

            # Try Documents folder
            $localBin = "$env:USERPROFILE\bin"
            if (-not (Test-Path $localBin)) {
                New-Item -ItemType Directory -Path $localBin -Force | Out-Null
            }

            # Add to PATH if not already there
            $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            if ($userPath -notlike "*$localBin*") {
                Write-Host "Adding to PATH: $localBin" -ForegroundColor Yellow
                [Environment]::SetEnvironmentVariable("PATH", "$userPath;$localBin", "User")
                Write-Host "⚠️  You may need to restart your terminal for PATH changes to take effect" -ForegroundColor Yellow
            }
        }

        $batchFile = Join-Path $localBin "cloudmedic.bat"

        # Create batch file that calls Python with the tool
        $batchContent = @"
@echo off
python "$toolPath" %*
"@

        Set-Content -Path $batchFile -Value $batchContent
        Write-Host "✓ Created: $batchFile" -ForegroundColor Green
        Write-Host ""
        Write-Host "Run with: cloudmedic" -ForegroundColor Cyan
        Write-Host "Note: You may need to restart your terminal/PowerShell" -ForegroundColor Yellow
    }

    "2" {
        # Add tool directory to PATH (requires admin)
        Write-Host ""
        Write-Host "Adding tool directory to system PATH..." -ForegroundColor Yellow
        Write-Host "This requires administrator privileges" -ForegroundColor Yellow

        # Check if running as admin
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

        if (-not $isAdmin) {
            Write-Host "❌ This option requires administrator privileges" -ForegroundColor Red
            Write-Host "   Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
            Write-Host "   Or choose option 1 instead" -ForegroundColor Yellow
            exit 1
        }

        # Add to system PATH
        $systemPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($systemPath -notlike "*$scriptDir*") {
            [Environment]::SetEnvironmentVariable("PATH", "$systemPath;$scriptDir", "Machine")
            Write-Host "✓ Added to PATH: $scriptDir" -ForegroundColor Green
            Write-Host ""
            Write-Host "Run with: python support_medic_tool_windows.py" -ForegroundColor Cyan
            Write-Host "⚠️  You must restart your terminal for changes to take effect" -ForegroundColor Yellow
        } else {
            Write-Host "✓ Directory already in PATH" -ForegroundColor Green
        }
    }

    "3" {
        # Create desktop shortcut
        Write-Host ""
        Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow

        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = Join-Path $desktopPath "Cloud Medic Tool.lnk"

        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = "python"
        $Shortcut.Arguments = "`"$toolPath`""
        $Shortcut.WorkingDirectory = $scriptDir
        $Shortcut.Description = "Cloud Medic Assistant Tool"
        $Shortcut.Save()

        Write-Host "✓ Created shortcut on desktop" -ForegroundColor Green
        Write-Host ""
        Write-Host "Double-click the 'Cloud Medic Tool' icon on your desktop to run" -ForegroundColor Cyan
    }

    "4" {
        Write-Host ""
        Write-Host "No installation performed." -ForegroundColor Yellow
        Write-Host "Run manually with: python `"$toolPath`"" -ForegroundColor Cyan
    }

    default {
        Write-Host "Invalid option" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Requirements:" -ForegroundColor Yellow
Write-Host "  ✓ Python 3" -ForegroundColor Green
Write-Host "  ✓ kubectl" -ForegroundColor Green
Write-Host "  ✓ kubectx (optional but recommended)" -ForegroundColor Green
Write-Host "  ✓ colorama package (pip install colorama)" -ForegroundColor Green
Write-Host ""
Write-Host "For help, see README.md" -ForegroundColor Cyan
