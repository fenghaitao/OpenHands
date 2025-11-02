# MCP Server Troubleshooting Guide

## Problem Summary

When running `openhands` CLI, you may encounter an EPIPE error or TimeoutError related to MCP (Model Context Protocol) servers:

```
Error: write EPIPE
  errno: -32,
  code: 'EPIPE',
  syscall: 'write'
```

or

```
TimeoutError
```

## Root Cause

The error occurs when:
1. An MCP stdio server crashes or exits unexpectedly during initialization
2. The MCP SDK tries to write to the closed pipe, resulting in an EPIPE error
3. The SDK times out (30s) waiting for a response from the crashed server

In your case, you have two MCP servers configured:
- **fetch**: `uvx mcp-server-fetch`
- **repomix**: `npx -y repomix@1.4.2 --mcp`

One or both of these servers is failing to initialize properly.

## Quick Fix: Disable MCP Servers Temporarily

We've created a utility script to temporarily disable MCP servers:

```bash
# Disable MCP servers
.venv/bin/python disable_mcp_servers.py

# This will:
# 1. Create a backup of your agent_settings.json
# 2. Remove the mcp_config section
# 3. Allow you to use OpenHands CLI without MCP servers
```

To restore MCP servers later:

```bash
# Restore from backup
.venv/bin/python disable_mcp_servers.py restore

# Or manually:
cp ~/.openhands/agent_settings.json.backup ~/.openhands/agent_settings.json
```

## Permanent Fix: Debug Individual MCP Servers

### Step 1: Test Each Server Manually

Test the fetch server:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | uvx mcp-server-fetch
```

Test the repomix server:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | npx -y repomix@1.4.2 --mcp
```

### Step 2: Identify the Problematic Server

Watch for:
- Servers that crash immediately
- Servers that hang without responding
- Error messages in the output

### Step 3: Fix or Remove the Problematic Server

Edit `~/.openhands/agent_settings.json` and either:

**Option A: Remove the problematic server**
```json
{
  "mcp_config": {
    "mcpServers": {
      "fetch": {
        "command": "uvx",
        "args": ["mcp-server-fetch"]
      }
      // Remove the problematic server
    }
  }
}
```

**Option B: Fix the server configuration**
- Check if the package is installed correctly
- Verify the command and arguments are correct
- Check for version compatibility issues

## Common Issues

### 1. Package Not Installed
```bash
# Install missing packages
npm install -g repomix@1.4.2
# or
uvx --help  # Verify uvx is installed
```

### 2. Version Incompatibility
Try different versions:
```bash
npx -y repomix@latest --mcp
```

### 3. Network Issues
Some MCP servers may require network access during initialization. Check your internet connection.

## Improvements Made

We've added better error handling to `openhands_cli/setup.py`:
- Detects EPIPE and TimeoutError during MCP server initialization
- Provides helpful error messages with troubleshooting steps
- Lists all configured MCP servers for easy debugging
- Suggests manual testing and quick fixes

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Configuration](https://gofastmcp.com/clients/client#configuration-format)
- [OpenHands MCP Guide](https://docs.all-hands.dev/usage/how-to/cli-mode#using-mcp-servers)

## Testing Your Fix

After making changes, test the CLI:

```bash
# Test without MCP servers (should work)
.venv/bin/openhands --help

# Test with MCP servers restored
.venv/bin/python disable_mcp_servers.py restore
.venv/bin/openhands
```

If the error persists, repeat the debugging steps above to identify which server is causing the issue.
