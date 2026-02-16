#!/bin/bash
# Build DupPicFinder natively for the current system
# This creates an executable optimized for your current Linux distribution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Building DupPicFinder - Native Build                 ║"
echo "║  Target: Current System ($(lsb_release -rs 2>/dev/null || echo 'Unknown'))                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo ""
    echo "Please create it first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📥 Installing PyInstaller..."
    pip install pyinstaller
fi

# Show system information
echo ""
echo "🖥️  Build System Information:"
echo "   OS: $(cat /etc/os-release | grep "^PRETTY_NAME=" | cut -d'"' -f2)"
echo "   GLIBC: $(ldd --version | head -1 | awk '{print $NF}')"
echo "   Python: $(python --version)"
echo ""

# Clean previous build artifacts (preserve dist/dockerBuild/)
echo "🧹 Cleaning previous build..."
rm -rf "$SCRIPT_DIR/build"

# Only remove the DupPicFinder executable, not the entire dist directory
# This preserves dist/dockerBuild/ and other build infrastructure
if [ -f "$SCRIPT_DIR/dist/DupPicFinder" ]; then
    rm -f "$SCRIPT_DIR/dist/DupPicFinder"
fi

# Build executable
echo "🔨 Building executable with PyInstaller..."
echo ""
pyinstaller --clean DupPicFinder.spec

# Check if build succeeded
if [ -f "$SCRIPT_DIR/dist/DupPicFinder" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📊 Executable information:"
    ls -lh "$SCRIPT_DIR/dist/DupPicFinder"
    file "$SCRIPT_DIR/dist/DupPicFinder"
    echo ""
    echo "🎯 Target compatibility:"
    GLIBC_VERSION=$(ldd --version | head -1 | awk '{print $NF}')
    echo "   • Systems with GLIBC $GLIBC_VERSION or newer"
    echo "   • $(lsb_release -ds 2>/dev/null || echo 'Current system') or newer"
    echo ""
    echo "📁 Location: $SCRIPT_DIR/dist/DupPicFinder"
    echo ""
    echo "💡 To test:"
    echo "   cd $SCRIPT_DIR/dist"
    echo "   ./DupPicFinder"
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
