# GitHub Copilot Auto-Setup for OpenHands

This feature automatically configures GitHub Copilot settings to avoid UI prompts for provider setup in both CLI and web modes.

## Quick Start

### ⚠️ Authentication Required First

**Before any setup**, you **must** authenticate with GitHub Copilot:

```bash
# Step 1: Authenticate (required before any setup)
openhands auth github-copilot

# Step 2: Verify authentication
openhands auth github-copilot --status
```

### Configuration Steps

1. **Configure GitHub Copilot** in your `config.toml`:
   ```toml
   [llm]
   model = "github_copilot/gpt-4.1"
   custom_llm_provider = "github_copilot"
   ```

2. **Run the setup command with your config file**:
   ```bash
   openhands github-copilot-init --config-file ./config_github_copilot_llm_direct.toml
   ```

3. **Start OpenHands** - settings will be auto-configured:
   ```bash
   openhands --config-file ./config_github_copilot_llm_direct.toml

   ```

## How It Works

### Automatic Detection
- Detects GitHub Copilot configuration from `config.toml`
- Determines mode (direct/proxy) automatically
- Creates `settings.json` with appropriate configuration
- Works for both CLI and web UI startup

### Manual Setup
```bash
# Auto-detect and setup
openhands github-copilot-init

# Specify mode
openhands github-copilot-init --mode direct
openhands github-copilot-init --mode proxy

# Force overwrite existing settings
openhands github-copilot-init --force
```

## Configuration Examples

### Direct Mode
```toml
[llm]
model = "github_copilot/gpt-4.1"
custom_llm_provider = "github_copilot"
```

### Proxy Mode
```toml
[core]
file_store_path = "~/.openhands/llm_proxy"

[llm]
model = "litellm_proxy/github_copilot/gpt-4.1"
base_url = "http://localhost:4000"
custom_llm_provider = "github_copilot"
```

## Implementation Details

### Files Added/Modified

1. **`openhands/cli/github_copilot_setup.py`** - Core setup functionality
2. **`openhands/cli/commands/github_copilot_init.py`** - CLI command
3. **`openhands/server/github_copilot_startup.py`** - Server startup hook
4. **`openhands/cli/main.py`** - CLI integration
5. **`openhands/server/app.py`** - Server integration

### Key Functions

- `detect_github_copilot_config()` - Detects GitHub Copilot configuration
- `detect_github_copilot_mode()` - Determines direct vs proxy mode
- `create_github_copilot_settings()` - Creates Settings object
- `setup_github_copilot_settings()` - Main setup function

### Integration Points

- **CLI startup**: Auto-setup before settings load
- **Server startup**: Auto-setup during FastAPI lifespan
- **Manual command**: `openhands github-copilot-init`

## Benefits

- ✅ **No UI prompts** for GitHub Copilot provider setup
- ✅ **Works for both modes** (direct and proxy)
- ✅ **Automatic detection** from existing configuration
- ✅ **Secure authentication** using existing methods
- ✅ **Consistent experience** across CLI and web UI

## Testing

Run the test suite:
```bash
python tmp_rovodev_test_github_copilot_setup.py
```

## Troubleshooting

### Common Issues

1. **No auto-setup occurring**:
   - Check `custom_llm_provider = "github_copilot"` is set
   - Verify GitHub Copilot model name format
   - Ensure valid authentication exists

2. **Settings not applied**:
   - Check `settings.json` exists in file store path
   - Verify file contains valid JSON
   - Restart OpenHands

3. **Authentication issues**:
   - Run `openhands auth github-copilot --status`
   - Check `GITHUB_TOKEN` environment variable
   - Verify OAuth token is valid

### Debug Commands

```bash
# Check configuration
python validate_github_copilot.py

# Test setup (dry run)
openhands github-copilot-init --dry-run

# Check authentication
openhands auth github-copilot --status
```

## Future Enhancements

- Support for multiple user configurations
- Integration with other LLM providers
- Advanced mode detection based on network configuration
- Settings migration from existing configurations
