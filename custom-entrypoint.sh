#!/bin/bash
# Custom entrypoint to apply proxy patches before starting OpenHands

# Apply the httpx timeout patch by adding it to Python's sitecustomize
mkdir -p /custom-patches
cat > /custom-patches/sitecustomize.py << 'EOF'
import httpx

# Store original AsyncClient
_original_async_client = httpx.AsyncClient

# Create patched version with longer timeout
class PatchedAsyncClient(_original_async_client):
    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = httpx.Timeout(30.0)
        super().__init__(*args, **kwargs)

# Replace httpx.AsyncClient with patched version
httpx.AsyncClient = PatchedAsyncClient
EOF

export PYTHONPATH="/custom-patches:${PYTHONPATH}"

# Run the original entrypoint
exec /app/entrypoint.sh "$@"
