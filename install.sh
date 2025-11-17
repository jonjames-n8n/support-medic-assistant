#!/bin/bash
# Quick installation script for Cloud Medic Tool

echo "=========================================="
echo "Cloud Medic Tool - Quick Install"
echo "=========================================="
echo

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found"

# Check for kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

echo "✓ kubectl found"

# Check for kubectx
if ! command -v kubectx &> /dev/null; then
    echo "⚠️  kubectx not found. Install it with: brew install kubectx"
    read -p "Continue anyway? (y/n): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ kubectx found"
fi

echo

# Get script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH="$SCRIPT_DIR/support_medic_tool.py"

if [ ! -f "$TOOL_PATH" ]; then
    echo "❌ support_medic_tool.py not found in current directory"
    exit 1
fi

# Make executable
chmod +x "$TOOL_PATH"
echo "✓ Made tool executable"

# Offer installation options
echo
echo "Installation options:"
echo "1. Install globally (requires sudo) - run as 'cloudmedic'"
echo "2. Create alias only - run as 'cloudmedic'"
echo "3. Skip - run manually with 'python3 support_medic_tool.py'"
echo

read -p "Choose option (1/2/3): " option

case $option in
    1)
        echo
        echo "Installing to /usr/local/bin/cloudmedic..."
        sudo cp "$TOOL_PATH" /usr/local/bin/cloudmedic
        echo "✓ Installed! Run with: cloudmedic"
        ;;
    2)
        SHELL_RC=""
        if [ -f "$HOME/.zshrc" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            echo "❌ Could not find .zshrc or .bashrc"
            exit 1
        fi
        
        echo
        echo "Adding alias to $SHELL_RC..."
        echo "alias cloudmedic=\"python3 $TOOL_PATH\"" >> "$SHELL_RC"
        echo "✓ Alias added!"
        echo
        echo "Run: source $SHELL_RC"
        echo "Then run: cloudmedic"
        ;;
    3)
        echo
        echo "No installation performed."
        echo "Run with: python3 $TOOL_PATH"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
