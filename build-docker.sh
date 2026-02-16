#!/bin/bash
# Wrapper script to build Docker distribution from project root

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Building Docker distribution (Ubuntu 20.04 compatible)..."
echo ""

# Run the Docker build script
"$SCRIPT_DIR/packaging/docker/ubuntu-20.04/build.sh"
