# GitHub Copilot OAuth Implementation for OpenHands

This implementation provides complete GitHub Copilot integration with OAuth authentication for OpenHands, leveraging LiteLLM's proven authenticator while providing a seamless user experience.

## 🚀 Features

✅ **Complete OAuth Flow**: Full GitHub device flow authentication  
✅ **LiteLLM Integration**: Uses LiteLLM's GitHub Copilot authenticator  
✅ **Automatic Token Management**: Handles token refresh and caching  
✅ **CLI Authentication**: Easy-to-use CLI commands  
✅ **Seamless LLM Integration**: Works with all OpenHands agents  
✅ **Fallback Support**: Falls back to GITHUB_TOKEN if OAuth unavailable  
✅ **Comprehensive Error Handling**: Clear error messages and recovery  

## 🔧 Implementation Overview

### Core Components

1. **`openhands/llm/github_copilot_auth.py`** - OAuth authentication manager
   - Wraps LiteLLM's GitHub Copilot authenticator
   - Provides device flow authentication
   - Handles token caching and refresh
   - Manages authentication state

2. **`openhands/llm/github_copilot.py`** - Provider configuration
   - Integrates OAuth with LLM configuration
   - Handles model detection and setup
   - Provides LiteLLM parameter generation
   - Validates authentication

3. **`openhands/cli/auth.py`** - CLI authentication commands
   - Interactive OAuth flow
   - Status checking and management
   - Token revocation
   - User-friendly interface

4. **`openhands/llm/llm.py`** - LLM integration
   - Automatic GitHub Copilot detection
   - OAuth token injection
   - Required headers setup
   - Error handling

## 🔐 Authentication Flow

### 1. OAuth Device Flow
```bash
# Start authentication
openhands auth github-copilot

# Check status
openhands auth github-copilot --status

# Revoke authentication
openhands auth github-copilot --revoke
```

### 2. Automatic Integration
```python
from openhands.core.config import LLMConfig
from openhands.llm import LLM

# OAuth token automatically used if available
config = LLMConfig(model="github_copilot/gpt-4.1")
llm = LLM(config)  # Uses OAuth token automatically
```

### 3. Environment Variable Fallback
```bash
# Fallback to environment variable
export GITHUB_TOKEN="your_token_here"
openhands --model github_copilot/gpt-4.1
```

## 📋 Usage Examples

### CLI Usage
```bash
# Authenticate with GitHub Copilot
openhands auth github-copilot

# Use GitHub Copilot model
openhands --model github_copilot/gpt-4.1

# Check authentication status
openhands auth github-copilot --check-only
```

### Python API Usage
```python
import asyncio
from openhands.core.config import LLMConfig
from openhands.llm import LLM
from openhands.llm.github_copilot_auth import GitHubCopilotAuthManager

async def main():
    # Authenticate if needed
    auth_manager = GitHubCopilotAuthManager()
    if not auth_manager.is_authenticated():
        success = await auth_manager.authenticate_async()
        if not success:
            print("Authentication failed")
            return
    
    # Use GitHub Copilot
    config = LLMConfig(model="github_copilot/gpt-4.1")
    llm = LLM(config)
    
    response = llm.completion(
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

### Configuration File
```toml
[llm]
model = "github_copilot/gpt-4.1"
custom_llm_provider = "github_copilot"
temperature = 0.0
max_output_tokens = 4096
```

## 🔄 How It Works

### 1. Model Detection
When a `github_copilot/` model is specified:
- `GitHubCopilotConfig.is_github_copilot_model()` detects it
- Configuration is automatically applied
- OAuth authentication is attempted

### 2. Authentication Priority
1. **Existing API Key**: Uses provided `api_key` if available
2. **OAuth Token**: Attempts to get token from OAuth authentication
3. **Environment Variable**: Falls back to `GITHUB_TOKEN`
4. **Error**: Clear error message if no authentication available

### 3. LiteLLM Integration
- Uses LiteLLM's `github_copilot` provider
- Adds required headers automatically
- Handles token refresh through LiteLLM
- Provides proper error handling

### 4. Token Management
- Tokens cached in `~/.config/openhands/github_copilot/`
- Automatic refresh when expired
- Secure storage and handling
- Easy revocation and cleanup

## 🛠️ Technical Details

### Authentication Manager
```python
class GitHubCopilotAuthManager:
    def __init__(self, token_dir: Optional[str] = None)
    def is_authenticated(self) -> bool
    def get_api_key(self) -> Optional[str]
    def authenticate(self, timeout: int = 900) -> bool
    def authenticate_async(self, timeout: int = 900) -> bool
    def revoke_authentication(self) -> None
    def get_auth_status(self) -> Dict[str, Any]
```

### Configuration Helper
```python
class GitHubCopilotConfig:
    @classmethod
    def is_github_copilot_model(cls, model: str) -> bool
    
    @classmethod
    def configure_for_copilot(cls, config: LLMConfig) -> LLMConfig
    
    @classmethod
    def get_litellm_params(cls, config: LLMConfig) -> Dict[str, Any]
```

### CLI Commands
```bash
openhands auth github-copilot [OPTIONS]

Options:
  --timeout INTEGER     Maximum time to wait for authentication
  --token-dir TEXT      Directory to store authentication tokens
  --check-only          Only check authentication status
  --revoke              Revoke existing authentication
  --status              Show detailed authentication status
```

## 🔍 Error Handling

### Common Scenarios
1. **No Authentication**: Clear instructions to authenticate
2. **Expired Tokens**: Automatic refresh or re-authentication prompt
3. **Network Issues**: Retry logic and timeout handling
4. **Invalid Subscription**: Clear error about Copilot access
5. **LiteLLM Unavailable**: Graceful fallback to environment variables

### Error Messages
```
❌ Invalid GitHub Copilot configuration. 
   Run 'openhands auth github-copilot' to authenticate or 
   set GITHUB_TOKEN environment variable.
```

## 🧪 Testing

### Run the Example
```bash
python examples/github_copilot_oauth_example.py
```

### Test Authentication
```bash
# Test authentication flow
openhands auth github-copilot --check-only

# Test with model
openhands --model github_copilot/gpt-4.1 --task "Write a hello world function"
```

### Verify Integration
```python
from openhands.llm.github_copilot import GitHubCopilotConfig
from openhands.core.config import LLMConfig

# Test configuration
config = LLMConfig(model="github_copilot/gpt-4.1")
assert GitHubCopilotConfig.is_github_copilot_model(config.model)

configured = GitHubCopilotConfig.configure_for_copilot(config)
assert configured.custom_llm_provider == "github_copilot"
```

## 🔒 Security Considerations

- **Token Storage**: Tokens stored securely in user config directory
- **No Hardcoded Secrets**: No client secrets in code
- **Minimal Permissions**: Only requests necessary OAuth scopes
- **Automatic Cleanup**: Easy token revocation and cleanup
- **Environment Isolation**: Separate token storage per user

## 🚀 Future Enhancements

1. **Web OAuth Flow**: Alternative to device flow for web environments
2. **Token Sharing**: Share tokens across OpenHands instances
3. **Advanced Caching**: More sophisticated token caching strategies
4. **Usage Tracking**: Integration with GitHub usage metrics
5. **Enterprise Support**: Support for GitHub Enterprise instances

## 📚 Dependencies

- **LiteLLM**: For GitHub Copilot provider and authentication
- **Click**: For CLI interface
- **httpx**: For HTTP requests (via LiteLLM)
- **Pydantic**: For configuration validation

## 🎯 Benefits

1. **User Experience**: Simple, guided authentication process
2. **Developer Experience**: Seamless integration with existing code
3. **Reliability**: Leverages proven LiteLLM authenticator
4. **Flexibility**: Multiple authentication methods
5. **Maintainability**: Clean separation of concerns
6. **Extensibility**: Easy to extend for other OAuth providers

This implementation provides a production-ready GitHub Copilot integration that handles the complexity of OAuth authentication while providing a simple, intuitive user experience.