# Cloud Medic Assistant Tool - Windows Edition

Interactive CLI tool for n8n Cloud support operations, optimized for Windows.

## 🪟 Windows-Specific Features

This Windows edition has been specifically adapted for Windows environments:

- ✅ **No shell dependencies** - Uses direct subprocess calls instead of shell=True
- ✅ **Cross-platform paths** - Uses Python's pathlib for all file operations
- ✅ **Native compression** - Uses Python's tarfile and gzip modules instead of Unix commands
- ✅ **Windows terminal colors** - Full color support via colorama
- ✅ **PowerShell installer** - Easy setup with install.ps1

## 📋 Prerequisites

### Required

1. **Python 3.7+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **kubectl** - Kubernetes command-line tool
   - Download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
   - Or install via Chocolatey: `choco install kubernetes-cli`

3. **colorama** - Python package for terminal colors
   ```powershell
   pip install colorama
   ```

### Optional but Recommended

4. **kubectx** - Context switching tool
   - Download from: https://github.com/ahmetb/kubectx
   - Install via Chocolatey: `choco install kubectx`
   - Or install manually and add to PATH

## 🚀 Quick Start

### Option 1: PowerShell Installer (Recommended)

1. Open PowerShell (no admin required)
2. Navigate to the tool directory:
   ```powershell
   cd path\to\support-medic-assistant
   ```
3. Run the installer:
   ```powershell
   .\install.ps1
   ```
4. Choose installation option (option 1 recommended)
5. Run the tool:
   ```powershell
   cloudmedic
   ```

### Option 2: Manual Run

```powershell
python support_medic_tool_windows.py
```

## 💾 Installation Options

The PowerShell installer (`install.ps1`) offers four options:

### 1. Create Batch File (Recommended) ⭐
- Creates `cloudmedic.bat` in `%LOCALAPPDATA%\Microsoft\WindowsApps`
- No admin privileges required
- Accessible from any directory
- Run with: `cloudmedic`

### 2. Add to System PATH
- Requires administrator privileges
- Adds tool directory to system PATH
- Requires terminal restart
- Run with: `python support_medic_tool_windows.py`

### 3. Desktop Shortcut
- Creates clickable shortcut on desktop
- No admin privileges required
- Double-click to run

### 4. Skip Installation
- Run manually each time
- No installation needed

## 🎯 Usage

Once installed, the tool works identically to the Linux/Mac version:

```powershell
cloudmedic
```

### Main Features

- **0** - Health check (pod status, DB size, recent errors)
- **1-2** - Export workflows (live or from backup)
- **3** - Import workflows
- **4-5** - Deactivate workflows (all or specific)
- **6-8** - Execution management (check, cancel pending/waiting)
- **9-12** - Maintenance (backup, logs, DB troubleshooting, redeploy)
- **14** - Download logs (n8n, backup, k8s, execution, bundle)
- **15** - Disable 2FA
- **16** - Change owner email

## 📁 File Locations

The Windows version uses standard Windows paths:

- **Downloads**: `%USERPROFILE%\Downloads`
- **Temp files**: `%TEMP%` (via Python's tempfile module)
- **Batch file**: `%LOCALAPPDATA%\Microsoft\WindowsApps\cloudmedic.bat`

## 🔧 Troubleshooting

### "python is not recognized..."

**Solution**: Add Python to PATH
1. Search for "Environment Variables" in Windows
2. Edit "Path" under User Variables
3. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X`
4. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\Scripts`
5. Restart terminal

### "kubectl is not recognized..."

**Solution**: Install kubectl or add to PATH
- Download kubectl.exe and place in `C:\Program Files\kubectl\`
- Add that directory to PATH (see above)
- Or use Chocolatey: `choco install kubernetes-cli`

### Colors not working

**Solution**: Install colorama
```powershell
pip install colorama
```

### "Execution policy" error when running install.ps1

**Solution**: Temporarily allow script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run the installer again.

### "cloudmedic" command not found

**Solutions**:
1. Restart your terminal/PowerShell
2. Verify batch file exists: `dir %LOCALAPPDATA%\Microsoft\WindowsApps\cloudmedic.bat`
3. Check PATH includes WindowsApps: `echo %PATH%`
4. Re-run installer and choose option 1

## 🆚 Differences from Unix Version

The Windows edition has these differences:

| Feature | Unix Version | Windows Version |
|---------|-------------|-----------------|
| Shell execution | Uses `shell=True` | Direct subprocess calls |
| File compression | Uses `tar`, `gzip` commands | Python tarfile/gzip modules |
| File size | Uses `du -sh` command | Python Path.stat() |
| Text processing | Uses `awk` command | Python string operations |
| Installation | Copies to `/usr/local/bin` | Batch file or PATH |
| Script file | `support_medic_tool.py` | `support_medic_tool_windows.py` |

## 🧪 Testing

To verify your installation:

1. Check Python version:
   ```powershell
   python --version
   ```
   Should show Python 3.7 or higher

2. Check kubectl:
   ```powershell
   kubectl version --client
   ```

3. Check colorama:
   ```powershell
   pip show colorama
   ```

4. Run the tool:
   ```powershell
   cloudmedic
   ```
   or
   ```powershell
   python support_medic_tool_windows.py
   ```

## 📚 Additional Documentation

- **README.md** - General tool documentation and features
- **QUICK_START.md** - Quick reference guide
- **CHANGELOG.md** - Version history

## 🐛 Known Limitations

1. **Interactive database shell** (Option 11 → 9) may have display issues in PowerShell
   - Use Windows Terminal for best experience

2. **kubectx** on Windows may require additional setup
   - Consider using kubectl config use-context instead

3. **VPN** connectivity required for kubectl access
   - Ensure VPN is connected before running

## 💡 Tips for Windows Users

1. **Use Windows Terminal** instead of Command Prompt for better colors
2. **Run as regular user** - Admin not required (except option 2)
3. **Keep terminal open** while operations are running
4. **Check Downloads folder** for exported files
5. **Use Tab completion** in PowerShell for faster navigation

## 🤝 Support

For issues specific to the Windows version:

1. Check this README for troubleshooting
2. Verify all prerequisites are installed
3. Try running with `python -v` for verbose output
4. Check that colorama is installed: `pip list | findstr colorama`

## 📄 License

Same license as the main Cloud Medic Tool.

## 🔄 Updates

To update the Windows version:

1. Pull latest changes from repository
2. Re-run `install.ps1` if needed
3. No need to uninstall first

---

**Version**: 1.2.1 (Windows Edition)
**Last Updated**: 2024-11-24
