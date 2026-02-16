#!/bin/bash
# Build DupPicFinder for Ubuntu 20.04 (GLIBC 2.31) using Docker
# This creates a portable executable compatible with older Linux systems

set -e

# Get the project root (3 levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Building DupPicFinder for Ubuntu 20.04               ║"
echo "║  Target: GLIBC 2.31+ (Maximum Compatibility)          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Project root: $PROJECT_ROOT"
echo "Build dir:    $BUILD_DIR"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/engine/install/"
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image (this may take 10-15 minutes first time)..."
echo ""
docker build -f "$BUILD_DIR/Dockerfile" -t duppicfinder-ubuntu2004 "$PROJECT_ROOT"

echo ""
echo "🔨 Building executable..."
echo ""

# Run build in container, output to this directory
docker run --rm \
    -v "$PROJECT_ROOT/src:/app/src" \
    -v "$PROJECT_ROOT/requirements.txt:/app/requirements.txt" \
    -v "$PROJECT_ROOT/DupPicFinder.spec:/app/DupPicFinder.spec" \
    -v "$BUILD_DIR:/app/output" \
    duppicfinder-ubuntu2004 \
    bash -c "pyinstaller --clean DupPicFinder.spec && cp dist/DupPicFinder /app/output/"

# Check if build succeeded
if [ -f "$BUILD_DIR/DupPicFinder" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📊 Executable information:"
    ls -lh "$BUILD_DIR/DupPicFinder"
    file "$BUILD_DIR/DupPicFinder"
    echo ""
    echo "🎯 Target compatibility:"
    echo "   • Ubuntu 20.04 LTS or newer"
    echo "   • Debian 11 or newer"
    echo "   • Linux Mint 20 or newer"
    echo "   • Any Linux with GLIBC 2.31+"
    echo ""
    echo "📁 Location: $BUILD_DIR/DupPicFinder"
    echo ""
    echo "💡 To test on target system:"
    echo "   1. Copy $BUILD_DIR/DupPicFinder to target machine"
    echo "   2. chmod +x DupPicFinder"
    echo "   3. ./DupPicFinder"
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
