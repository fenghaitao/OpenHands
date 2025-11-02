#!/bin/bash
# Script to update docker-compose.yml to use local runtime (Step 3 of building custom runtime)
# Usage: ./build_runtime_step3.sh

set -e

IMAGE_TAG="${IMAGE_TAG:-openhands-runtime:local}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

echo "================================================"
echo "Step 3: Update Docker Compose Configuration"
echo "================================================"
echo "Compose File: $COMPOSE_FILE"
echo "Image Tag: $IMAGE_TAG"
echo ""

# Check if docker-compose.yml exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "ERROR: $COMPOSE_FILE not found"
    exit 1
fi

# Check if the image exists
if ! docker image inspect "$IMAGE_TAG" &> /dev/null; then
    echo "WARNING: Image $IMAGE_TAG not found locally"
    echo "Please run step 2 first: ./build_runtime_step2.sh"
    exit 1
fi

# Backup the original file
BACKUP_FILE="${COMPOSE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "Creating backup: $BACKUP_FILE"
cp "$COMPOSE_FILE" "$BACKUP_FILE"

# Update the sandbox_image in docker-compose.yml
echo "Updating SANDBOX_RUNTIME_CONTAINER_IMAGE to use: $IMAGE_TAG"
sed -i "s|SANDBOX_RUNTIME_CONTAINER_IMAGE=.*|SANDBOX_RUNTIME_CONTAINER_IMAGE=$IMAGE_TAG|g" "$COMPOSE_FILE"

echo ""
echo "✓ Step 3 completed successfully!"
echo "Docker Compose has been updated to use: $IMAGE_TAG"
echo "Backup saved as: $BACKUP_FILE"
echo ""
echo "Next steps:"
echo "  1. Start OpenHands with your custom runtime:"
echo "     docker compose up -d"
echo "  2. Check logs if needed:"
echo "     docker compose logs -f"
echo ""
