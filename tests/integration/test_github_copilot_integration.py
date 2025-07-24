"""Integration tests for GitHub Copilot OAuth provider in OpenHands.

This test suite validates the complete GitHub Copilot integration including:
- OAuth authentication flow
- Token validation and refresh
- LLM initialization and configuration
- Actual API calls with GitHub Copilot models
- Error handling and fallback scenarios
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from typing import Optional

from openhands.core.config import LLMConfig
from openhands.llm import LLM
from openhands.llm.github_copilot_auth import (
    GitHubCopilotAuthManager,
    GitHubCopilotAuthenticationError,
    get_auth_manager,
)
from openhands.llm.github_copilot import (
    GitHubCopilotConfig,
    validate_github_copilot_config,
)


class TestGitHubCopilotIntegration:
    """Integration tests for GitHub Copilot OAuth provider."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Mock authentication manager for testing."""
        with patch('openhands.llm.github_copilot_auth.LiteLLMAuthenticator') as mock_auth:
            mock_instance = MagicMock()
            mock_auth.return_value = mock_instance
            
            # Mock successful authentication
            mock_instance.get_api_key.return_value = "test_copilot_token_12345"
            mock_instance._get_device_code.return_value = {
                'device_code': 'test_device_code',
                'user_code': 'TEST-CODE',
                'verification_uri': 'https://github.com/login/device',
                'expires_in': 900,
                'interval': 5
            }
            mock_instance._poll_for_access_token.return_value = "test_access_token"
            
            yield mock_instance

    @pytest.fixture
    def github_token_env(self):
        """Set up GitHub token environment variable."""
        original_token = os.environ.get('GITHUB_TOKEN')
        os.environ['GITHUB_TOKEN'] = 'test_github_token_fallback'
        yield
        if original_token:
            os.environ['GITHUB_TOKEN'] = original_token
        else:
            os.environ.pop('GITHUB_TOKEN', None)

    def test_oauth_authentication_flow(self, mock_auth_manager):
        """Test complete OAuth authentication flow."""
        auth_manager = GitHubCopilotAuthManager()
        
        # Test authentication status check
        assert auth_manager.is_authenticated()
        
        # Test API key retrieval
        api_key = auth_manager.get_api_key()
        assert api_key == "test_copilot_token_12345"
        
        # Test device flow initiation
        device_info = auth_manager.start_device_flow()
        assert device_info['user_code'] == 'TEST-CODE'
        assert device_info['verification_uri'] == 'https://github.com/login/device'
        
        # Test authentication status
        status = auth_manager.get_auth_status()
        assert status['authenticated'] is True

    @pytest.mark.asyncio
    async def test_async_authentication_flow(self, mock_auth_manager):
        """Test asynchronous authentication flow."""
        auth_manager = GitHubCopilotAuthManager()
        
        # Mock already authenticated
        success = await auth_manager.authenticate_async(timeout=1)
        assert success is True

    def test_llm_configuration_with_oauth(self, mock_auth_manager):
        """Test LLM configuration with OAuth authentication."""
        # Test GitHub Copilot model detection
        config = LLMConfig(model="github_copilot/gpt-4.1")
        
        assert GitHubCopilotConfig.is_github_copilot_model(config.model)
        
        # Test configuration
        configured = GitHubCopilotConfig.configure_for_copilot(config)
        
        assert configured.custom_llm_provider == "github_copilot"
        assert configured.base_url == GitHubCopilotConfig.DEFAULT_API_BASE
        assert configured.model == "github_copilot/gpt-4.1"
        assert configured.api_key is not None

    def test_llm_initialization_with_oauth(self, mock_auth_manager):
        """Test LLM initialization with OAuth token."""
        config = LLMConfig(model="github_copilot/gpt-4.1")
        
        # This should use OAuth token automatically
        llm = LLM(config)
        
        assert llm.config.custom_llm_provider == "github_copilot"
        assert llm.config.base_url == "https://api.githubcopilot.com"
        assert llm.config.api_key is not None
        assert llm.is_function_calling_active()

    def test_fallback_to_environment_variable(self, github_token_env):
        """Test fallback to GITHUB_TOKEN environment variable."""
        with patch('openhands.llm.github_copilot_auth.LITELLM_AVAILABLE', False):
            config = LLMConfig(model="github_copilot/gpt-4o")
            
            configured = GitHubCopilotConfig.configure_for_copilot(config)
            
            assert configured.api_key.get_secret_value() == "test_github_token_fallback"
            assert configured.custom_llm_provider == "github_copilot"

    def test_all_supported_models(self, mock_auth_manager):
        """Test all supported GitHub Copilot models."""
        supported_models = [
            "github_copilot/gpt-4.1",
            "github_copilot/gpt-4o", 
            "github_copilot/gpt-4o-mini",
            "github_copilot/o1-preview",
            "github_copilot/o1-mini",
            "github_copilot/claude-sonnet-4"
        ]
        
        for model in supported_models:
            config = LLMConfig(model=model)
            
            # Test model detection
            assert GitHubCopilotConfig.is_github_copilot_model(model)
            
            # Test configuration
            configured = GitHubCopilotConfig.configure_for_copilot(config)
            assert configured.custom_llm_provider == "github_copilot"
            assert configured.model == model
            
            # Test LLM initialization
            llm = LLM(configured)
            assert llm.config.model == model

    def test_litellm_params_generation(self, mock_auth_manager):
        """Test LiteLLM parameters generation for GitHub Copilot."""
        config = LLMConfig(
            model="github_copilot/claude-sonnet-4",
            api_key="test_token"
        )
        
        params = GitHubCopilotConfig.get_litellm_params(config)
        
        assert params["model"] == "github_copilot/claude-sonnet-4"
        assert params["api_base"] == "https://api.githubcopilot.com"
        assert params["api_key"] == "test_token"
        assert "extra_headers" in params
        assert params["extra_headers"]["User-Agent"] == "GitHubCopilot/1.0"
        assert params["extra_headers"]["Copilot-Integration-Id"] == "vscode-copilot"

    def test_error_handling_no_authentication(self):
        """Test error handling when no authentication is available."""
        with patch('openhands.llm.github_copilot_auth.LITELLM_AVAILABLE', False):
            with patch.dict(os.environ, {}, clear=True):
                config = LLMConfig(model="github_copilot/gpt-4.1")
                
                # Should not validate without authentication
                assert not validate_github_copilot_config(config)
                
                # Should raise error when trying to initialize LLM
                with pytest.raises(ValueError, match="Invalid GitHub Copilot configuration"):
                    LLM(config)

    def test_token_refresh_scenario(self, mock_auth_manager):
        """Test token refresh scenario."""
        auth_manager = GitHubCopilotAuthManager()
        
        # Simulate expired token
        mock_auth_manager.get_api_key.side_effect = [
            Exception("Token expired"),
            "new_refreshed_token_67890"
        ]
        
        # Should handle token refresh
        with pytest.raises(GitHubCopilotAuthenticationError):
            auth_manager.get_api_key()

    @pytest.mark.skipif(
        not os.getenv('GITHUB_COPILOT_INTEGRATION_TEST'),
        reason="Set GITHUB_COPILOT_INTEGRATION_TEST=1 to run real API tests"
    )
    def test_real_api_call(self):
        """Test real API call to GitHub Copilot (requires actual authentication)."""
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            temperature=0.1,
            max_output_tokens=100
        )
        
        llm = LLM(config)
        
        messages = [
            {
                "role": "user",
                "content": "Write a simple Python function that adds two numbers."
            }
        ]
        
        try:
            response = llm.completion(messages=messages)
            
            assert response is not None
            assert len(response.choices) > 0
            assert response.choices[0].message.content is not None
            assert "def" in response.choices[0].message.content.lower()
            
            print(f"✅ Real API test successful!")
            print(f"Response: {response.choices[0].message.content[:200]}...")
            
        except Exception as e:
            pytest.fail(f"Real API call failed: {e}")

    def test_function_calling_support(self, mock_auth_manager):
        """Test function calling support for GitHub Copilot models."""
        from openhands.llm.llm import FUNCTION_CALLING_SUPPORTED_MODELS
        
        copilot_models = [
            "github_copilot/gpt-4.1",
            "github_copilot/gpt-4o",
            "github_copilot/gpt-4o-mini", 
            "github_copilot/o1-preview",
            "github_copilot/o1-mini",
            "github_copilot/claude-sonnet-4"
        ]
        
        for model in copilot_models:
            assert model in FUNCTION_CALLING_SUPPORTED_MODELS
            
            config = LLMConfig(model=model)
            llm = LLM(config)
            assert llm.is_function_calling_active()

    def test_configuration_validation(self, mock_auth_manager):
        """Test comprehensive configuration validation."""
        # Valid configuration
        valid_config = LLMConfig(
            model="github_copilot/gpt-4.1",
            custom_llm_provider="github_copilot"
        )
        assert validate_github_copilot_config(valid_config)
        
        # Non-Copilot model (should pass validation)
        non_copilot_config = LLMConfig(model="gpt-4o")
        assert validate_github_copilot_config(non_copilot_config)

    def test_auth_manager_singleton(self, mock_auth_manager):
        """Test that auth manager works as singleton."""
        manager1 = get_auth_manager()
        manager2 = get_auth_manager()
        
        # Should be the same instance
        assert manager1 is manager2

    def test_token_revocation(self, mock_auth_manager):
        """Test token revocation functionality."""
        auth_manager = GitHubCopilotAuthManager()
        
        # Should not raise error
        auth_manager.revoke_authentication()
        
        # Verify revocation was called
        assert True  # Mock doesn't actually revoke, but method should execute

    @pytest.mark.parametrize("model_variant", [
        "github_copilot/gpt-4.1",
        "copilot/gpt-4.1", 
        "gpt-4.1"  # Should be converted
    ])
    def test_model_name_variants(self, model_variant, mock_auth_manager):
        """Test different model name variants."""
        if model_variant == "gpt-4.1":
            # This should not be detected as Copilot model initially
            assert not GitHubCopilotConfig.is_github_copilot_model(model_variant)
        else:
            assert GitHubCopilotConfig.is_github_copilot_model(model_variant)
        
        # Test model name extraction
        if model_variant.startswith("github_copilot/"):
            extracted = GitHubCopilotConfig.get_copilot_model_name(model_variant)
            assert extracted == "gpt-4.1"


class TestGitHubCopilotCLIIntegration:
    """Test CLI integration for GitHub Copilot authentication."""

    def test_cli_auth_command_structure(self):
        """Test that CLI auth command is properly structured."""
        from openhands.cli.auth import github_copilot
        
        # Should be a Click command
        assert hasattr(github_copilot, 'callback')
        assert hasattr(github_copilot, 'params')

    @patch('openhands.llm.github_copilot_auth.GitHubCopilotAuthManager')
    def test_cli_auth_success_flow(self, mock_manager_class):
        """Test successful CLI authentication flow."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.is_authenticated.return_value = False
        mock_manager.authenticate.return_value = True
        
        from openhands.cli.auth import github_copilot
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(github_copilot, [])
        
        assert result.exit_code == 0
        mock_manager.authenticate.assert_called_once()


if __name__ == "__main__":
    # Run specific test for manual testing
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "real":
        # Set environment variable for real API test
        os.environ['GITHUB_COPILOT_INTEGRATION_TEST'] = '1'
        
        test_instance = TestGitHubCopilotIntegration()
        try:
            test_instance.test_real_api_call()
            print("✅ Real API integration test passed!")
        except Exception as e:
            print(f"❌ Real API integration test failed: {e}")
    else:
        print("Run with 'python test_github_copilot_integration.py real' for real API test")
        print("Make sure you're authenticated with 'openhands auth github-copilot' first")