# LiteLLM Proxy Configuration for OpenHands

This document describes how to set up and configure a LiteLLM proxy server and connect OpenHands to it for accessing LLM models in a corporate network environment.

## Prerequisites

- Python 3.8.1+ (but not 3.9.7)
- `uv` package manager installed
- Docker and Docker Compose installed
- Corporate proxy configuration (if applicable)
- GitHub Copilot access (for GitHub Copilot models)
- IFLOW API key (for IFLOW models)

## Part 1: Setting Up LiteLLM Proxy Server

### 1.1 Install uv Package Manager

First, install `uv` if you haven't already:

```bash
# Install uv using pip
pip install uv

# Or install using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

### 1.2 Clone and Setup LiteLLM

Clone the LiteLLM repository:

```bash
cd ~
git clone https://github.com/fenghaitao/litellm.git
cd litellm
```

### 1.3 Create Virtual Environment and Install Dependencies

Use `uv` to create a virtual environment and install dependencies:

```bash
# Create virtual environment using uv
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install litellm with proxy extras using uv
uv pip install -e ".[proxy,extra_proxy]"
```

### 1.4 Configure Environment Variables

Set up the required environment variables:

```bash
# Set the LiteLLM master key (used for authentication)
export LITELLM_MASTER_KEY="your-secure-master-key-here"

# Set IFLOW API key (for IFLOW models)
export IFLOW_API_KEY="your-iflow-api-key"

# Optional: Add to your ~/.bashrc or ~/.zshrc for persistence
echo 'export LITELLM_MASTER_KEY="your-secure-master-key-here"' >> ~/.bashrc
echo 'export IFLOW_API_KEY="your-iflow-api-key"' >> ~/.bashrc
```

### 1.5 Configuration File

The repository includes a configuration file `litellm_github_copilot_iflow_config.yaml` that defines:

- **GitHub Copilot Models**: GPT-4.1, GPT-5, GPT-4o, Claude, Gemini, and more
- **IFLOW Models**: Qwen3-Coder
- **Embedding Models**: text-embedding-ada-002, text-embedding-3-small
- **Router Settings**: Timeout (60s), retries (3)
- **Proxy Settings**: Max tokens (128k), temperature (0.7)

Key configuration sections:

```yaml
model_list:
  # IFLOW Models
  - model_name: "Qwen3-Coder"
    litellm_params:
      model: "iflow/Qwen3-Coder"
      api_key: os.environ/IFLOW_API_KEY

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  allow_requests_on_db_unavailable: true

router_settings:
  timeout: 60
  num_retries: 3

litellm_settings:
  drop_params: true
  max_tokens: 128000
  temperature: 0.7
```

### 1.6 Start LiteLLM Proxy Server

Start the LiteLLM proxy server:

```bash
cd ~/litellm
.venv/bin/litellm --config ./litellm_github_copilot_iflow_config.yaml
```

The server will start on `http://0.0.0.0:4000` by default.

To run in the background:

```bash
nohup .venv/bin/litellm --config ./litellm_github_copilot_iflow_config.yaml > litellm.log 2>&1 &
```

Verify the server is running:

```bash
# Check if the process is running
ps aux | grep litellm

# Check if the port is listening
ss -tlnp | grep :4000

# Test the endpoint
curl -I http://localhost:4000
```

## Part 2: Configuring OpenHands

### 2.1 Model Configuration in OpenHands UI

When configuring OpenHands to use the LiteLLM proxy, use the following settings in the OpenHands UI:

1. **Custom Model**: `litellm_proxy/iflow/Qwen3-Coder`
2. **Base URL**: `http://host.docker.internal:4000`
3. **API Key**: Use the value of your `$LITELLM_MASTER_KEY` environment variable

#### Available Models

The LiteLLM proxy provides access to multiple model families:

**IFLOW Models:**
- `litellm_proxy/iflow/Qwen3-Coder` - Recommended for OpenHands

**GitHub Copilot Models:**
- `litellm_proxy/github_copilot/gpt-4.1` - Latest GPT-4.1
- `litellm_proxy/github_copilot/gpt-5` - GPT-5
- `litellm_proxy/github_copilot/gpt-4o` - GPT-4o
- `litellm_proxy/github_copilot/claude-sonnet-4.5` - Claude Sonnet 4.5
- `litellm_proxy/github_copilot/gemini-2.5-pro` - Gemini 2.5 Pro
- And many more (see configuration file for full list)

**Model Aliases:**
- `litellm_proxy/latest-gpt` → gpt-4.1
- `litellm_proxy/latest-claude` → claude-sonnet-4.5
- `litellm_proxy/fastest` → gpt-4o-mini
- `litellm_proxy/reasoning` → o3-mini

### 2.2 Why `host.docker.internal`?

The base URL uses `host.docker.internal:4000` instead of `localhost:4000` because:
- OpenHands runs inside a Docker container
- `localhost` inside the container refers to the container itself, not the host machine
- `host.docker.internal` is a special DNS name that resolves to the host machine from within Docker containers
- This is configured in `docker-compose.yml` via the `extra_hosts` setting

### 2.3 Docker Compose Configuration

The `docker-compose.yml` includes the following configuration to support LiteLLM proxy access:

```yaml
services:
  openhands:
    environment:
      # Proxy settings for corporate networks
      - http_proxy=${http_proxy:-}
      - https_proxy=${https_proxy:-}
      - no_proxy=${no_proxy:-localhost,127.0.0.1}
      - HTTP_PROXY=${http_proxy:-}
      - HTTPS_PROXY=${https_proxy:-}
      - NO_PROXY=${no_proxy:-localhost,127.0.0.1}
      - SANDBOX_RUNTIME_STARTUP_ENV_VARS={'HTTP_PROXY':'${http_proxy:-}','HTTPS_PROXY':'${https_proxy:-}','NO_PROXY':'${no_proxy:-localhost,127.0.0.1}'}
    ports:
      - "3000:3000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.openhands:/.openhands
      - ${WORKSPACE_BASE:-./workspace}:/opt/workspace_base
      - ./proxy-patch.py:/app/.venv/lib/python3.13/site-packages/sitecustomize.py:ro
```

### 2.4 Corporate Proxy Configuration

#### Timeout Patch

For corporate networks with proxy servers, HTTP requests may take longer to complete. The `proxy-patch.py` file increases the default timeout from 5 seconds to 120 seconds and is automatically loaded via sitecustomize.py.

#### NO_PROXY Settings

Ensure your `no_proxy` environment variable includes:
- `localhost,127.0.0.1` - Local addresses
- `host.docker.internal` - Docker host gateway
- Internal company domains (if applicable)
- Private network ranges: `10.0.0.0/8,192.168.0.0/16,172.16.0.0/12`

Example:
```bash
export no_proxy="localhost,127.0.0.1,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,host.docker.internal"
```

## Part 3: Verification and Testing

### 3.1 Verify LiteLLM Proxy Server

Before configuring OpenHands, verify that the LiteLLM proxy server is running and accessible:

```bash
# Check if the server is listening on all interfaces (0.0.0.0:4000)
ss -tlnp | grep :4000

# Expected output:
# LISTEN 0  2048  0.0.0.0:4000  0.0.0.0:*  users:(("litellm",pid=XXXXX,fd=14))

# Test the endpoint from host
curl -I http://localhost:4000

# Test from within the OpenHands container
docker exec openhands-app- curl -I http://host.docker.internal:4000
```

### 3.2 Test Model Access

Test that you can access models through the proxy:

```bash
# Test with curl (replace YOUR_MASTER_KEY with your actual key)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MASTER_KEY" \
  -d '{
    "model": "iflow/Qwen3-Coder",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 3.3 Monitor LiteLLM Logs

If running in the background, monitor the logs:

```bash
tail -f ~/litellm/litellm.log
```

## Part 4: Troubleshooting

### LiteLLM Server Issues

#### Server Not Starting

If the LiteLLM server fails to start:

1. **Check Python version**:
   ```bash
   python --version  # Should be 3.8.1+ but not 3.9.7
   ```

2. **Verify environment variables**:
   ```bash
   echo $LITELLM_MASTER_KEY
   echo $IFLOW_API_KEY
   ```

3. **Check for port conflicts**:
   ```bash
   ss -tlnp | grep :4000
   # If port is in use, kill the process or use a different port
   ```

4. **Review logs**:
   ```bash
   tail -f ~/litellm/litellm.log
   ```

#### Server Running but Not Accessible

1. **Verify server is listening on all interfaces**:
   ```bash
   ss -tlnp | grep :4000
   # Should show 0.0.0.0:4000, not 127.0.0.1:4000
   ```

2. **Check firewall rules** (if applicable)

### OpenHands Connection Issues

#### Connection Timeout

If you see "timed out" errors when starting a conversation:
1. Verify the LiteLLM proxy server is running: `ss -tlnp | grep :4000`
2. Check that the server is listening on `0.0.0.0:4000` (all interfaces), not just `127.0.0.1:4000`
3. Ensure the timeout patch is applied (check for `sitecustomize.py` in the container)
4. Verify proxy settings if in a corporate network

#### Connection Refused

If you see "Connection refused" errors:
1. Ensure the LiteLLM proxy server is running
2. Verify the base URL is set to `http://host.docker.internal:4000` (not `localhost`)
3. Check that `extra_hosts` is configured in `docker-compose.yml`

#### Authentication Errors

If you see "Authentication Error, No api key passed in":
1. Verify your `LITELLM_MASTER_KEY` environment variable is set
2. Enter the correct API key in the OpenHands UI settings
3. Restart OpenHands after updating the API key

## Part 5: Remote Access

For remote machines accessing OpenHands:

1. **Same configuration**: Use the same LiteLLM proxy settings
   - Custom Model: `litellm_proxy/iflow/Qwen3-Coder`
   - Base URL: `http://host.docker.internal:4000`
   - API Key: Your `$LITELLM_MASTER_KEY`

2. **Network requirements**:
   - The remote machine must be able to reach the OpenHands server
   - The LiteLLM proxy runs on the OpenHands host, not the remote client
   - All LLM requests are proxied through the OpenHands server

## Reference

For more information about LiteLLM proxy configuration, see:
- [OpenHands LiteLLM Proxy Documentation](https://docs.openhands.dev/openhands/usage/llms/litellm-proxy)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM GitHub Repository](https://github.com/BerriAI/litellm)
