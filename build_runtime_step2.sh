#!/bin/bash
# Script to build runtime Docker image (Step 2 of building custom runtime)
# Usage: ./build_runtime_step2.sh

set -e

BUILD_FOLDER="${BUILD_FOLDER:-containers/runtime}"
IMAGE_TAG="${IMAGE_TAG:-openhands-runtime:local}"

echo "================================================"
echo "Step 2: Build Runtime Docker Image"
echo "================================================"
echo "Build Folder: $BUILD_FOLDER"
echo "Image Tag: $IMAGE_TAG"
echo ""

# Check if Dockerfile exists
if [ ! -f "$BUILD_FOLDER/Dockerfile" ]; then
    echo "ERROR: Dockerfile not found in $BUILD_FOLDER"
    echo "Please run step 1 first: ./build_runtime_step1.sh"
    exit 1
fi

# Check if proxy variables are set
if [ -n "$http_proxy" ] || [ -n "$https_proxy" ]; then
    echo "Proxy settings detected:"
    echo "  HTTP_PROXY: ${http_proxy:-not set}"
    echo "  HTTPS_PROXY: ${https_proxy:-not set}"
    echo "  NO_PROXY: ${no_proxy:-not set}"
    echo ""
    
    # Build with proxy
    echo "Building with proxy configuration..."
    docker build \
        --build-arg HTTP_PROXY="$http_proxy" \
        --build-arg HTTPS_PROXY="$https_proxy" \
        --build-arg NO_PROXY="$no_proxy,deb.debian.org,security.debian.org" \
        --network host \
        -t "$IMAGE_TAG" \
        "$BUILD_FOLDER"
else
    echo "No proxy detected, building without proxy..."
    docker build \
        --network host \
        -t "$IMAGE_TAG" \
        "$BUILD_FOLDER"
fi

echo ""
echo "✓ Step 2 completed successfully!"
echo "Runtime image built: $IMAGE_TAG"
echo ""
echo "Next steps:"
echo "  3. Update docker-compose.yml to use local image:"
echo "     ./build_runtime_step3.sh"
echo ""
echo "Note: If the build failed due to proxy or timeout issues, you may need to:"
echo "  - Retry the build (network issues can be transient)"
echo "  - Adjust proxy settings"
echo "  - Use the pre-built image instead (recommended)"
