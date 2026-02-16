#!/bin/bash
# Build DupPicFinder for Ubuntu 20.04 (GLIBC 2.31) using Docker
# This creates a portable executable compatible with older Linux systems

set -e

# Get the project root (3 levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
OUTPUT_NAME="DupPicFinder-ubuntu-20.04"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Building DupPicFinder for Ubuntu 20.04               ║"
echo "║  Target: GLIBC 2.31+ (Maximum Compatibility)          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Project root: $PROJECT_ROOT"
echo "Output dir:   $DIST_DIR"
echo "Output name:  $OUTPUT_NAME"
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
docker build -f "$SCRIPT_DIR/Dockerfile" -t duppicfinder-ubuntu2004 "$PROJECT_ROOT"

echo ""
echo "🔨 Building executable..."
echo ""

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Run build in container, output to dist directory
docker run --rm \
    -v "$PROJECT_ROOT/src:/app/src" \
    -v "$PROJECT_ROOT/requirements.txt:/app/requirements.txt" \
    -v "$PROJECT_ROOT/DupPicFinder.spec:/app/DupPicFinder.spec" \
    -v "$DIST_DIR:/app/output" \
    duppicfinder-ubuntu2004 \
    bash -c "pyinstaller --clean DupPicFinder.spec && cp dist/DupPicFinder /app/output/$OUTPUT_NAME"

# Check if build succeeded
if [ -f "$DIST_DIR/$OUTPUT_NAME" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📊 Executable information:"
    ls -lh "$DIST_DIR/$OUTPUT_NAME"
    file "$DIST_DIR/$OUTPUT_NAME"
    echo ""
    echo "🎯 Target compatibility:"
    echo "   • Ubuntu 20.04 LTS or newer"
    echo "   • Debian 11 or newer"
    echo "   • Linux Mint 20 or newer"
    echo "   • Any Linux with GLIBC 2.31+"
    echo ""
    echo "📁 Location: $DIST_DIR/$OUTPUT_NAME"
    echo ""
    echo "💡 To test on target system:"
    echo "   1. Copy $DIST_DIR/$OUTPUT_NAME to target machine"
    echo "   2. chmod +x $OUTPUT_NAME"
    echo "   3. ./$OUTPUT_NAME"
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
