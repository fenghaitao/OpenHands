#!/bin/bash
# Script to generate runtime build files (Step 1 of building custom runtime)
# Usage: ./build_runtime_step1.sh

set -e

BASE_IMAGE="${BASE_IMAGE:-nikolaik/python-nodejs:python3.12-nodejs22}"
BUILD_FOLDER="${BUILD_FOLDER:-containers/runtime}"

echo "================================================"
echo "Step 1: Generate Runtime Build Files"
echo "================================================"
echo "Base Image: $BASE_IMAGE"
echo "Build Folder: $BUILD_FOLDER"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed."
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create build folder
echo "Creating build folder..."
mkdir -p "$BUILD_FOLDER"

# Generate runtime build files using uv
echo "Generating runtime build files with uv..."
echo "This will install openhands-ai and its dependencies..."

uvx --python 3.12 --from openhands-ai python -m openhands.runtime.utils.runtime_build \
    --base_image "$BASE_IMAGE" \
    --build_folder "$BUILD_FOLDER"

echo ""
echo "✓ Step 1 completed successfully!"
echo "Generated files are in: $BUILD_FOLDER/"
echo ""
echo "Next steps:"
echo "  2. Build the runtime image:"
echo "     ./build_runtime_step2.sh"
echo "  3. Update docker-compose.yml to use local image:"
echo "     ./build_runtime_step3.sh"
