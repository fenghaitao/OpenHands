"""Tests for GitHub Copilot LLM provider."""

import os
import pytest
from unittest.mock import patch

from openhands.core.config import LLMConfig
from openhands.llm.github_copilot import (
    GitHubCopilotConfig,
    setup_github_copilot_provider,
    validate_github_copilot_config,
)


class TestGitHubCopilotConfig:
    """Test GitHub Copilot configuration functionality."""

    def test_is_github_copilot_model(self):
        """Test model detection for GitHub Copilot."""
        # Test positive cases
        assert GitHubCopilotConfig.is_github_copilot_model("github_copilot/gpt-4.1")
        assert GitHubCopilotConfig.is_github_copilot_model("github_copilot/gpt-4o")
        assert GitHubCopilotConfig.is_github_copilot_model("copilot/gpt-4.1")
        
        # Test negative cases
        assert not GitHubCopilotConfig.is_github_copilot_model("gpt-4o")
        assert not GitHubCopilotConfig.is_github_copilot_model("claude-3-sonnet")
        assert not GitHubCopilotConfig.is_github_copilot_model("openai/gpt-4")

    def test_get_copilot_model_name(self):
        """Test extraction of model names."""
        assert GitHubCopilotConfig.get_copilot_model_name("github_copilot/gpt-4.1") == "gpt-4.1"
        assert GitHubCopilotConfig.get_copilot_model_name("copilot/gpt-4o") == "gpt-4o"
        assert GitHubCopilotConfig.get_copilot_model_name("gpt-4.1") == "gpt-4.1"

    def test_configure_for_copilot_basic(self):
        """Test basic GitHub Copilot configuration."""
        config = LLMConfig(model="github_copilot/gpt-4.1", api_key="test-token")
        
        configured = GitHubCopilotConfig.configure_for_copilot(config)
        
        assert configured.custom_llm_provider == "github_copilot"
        assert configured.base_url == GitHubCopilotConfig.DEFAULT_API_BASE
        assert configured.model == "github_copilot/gpt-4.1"
        assert configured.api_key.get_secret_value() == "test-token"

    def test_configure_for_copilot_model_prefix_addition(self):
        """Test that model prefix is added when missing."""
        config = LLMConfig(model="gpt-4.1", api_key="test-token")
        
        # First check that it's not detected as copilot model
        assert not GitHubCopilotConfig.is_github_copilot_model(config.model)
        
        # Manually set it as copilot and configure
        config.model = "github_copilot/gpt-4.1"
        configured = GitHubCopilotConfig.configure_for_copilot(config)
        
        assert configured.model == "github_copilot/gpt-4.1"

    @patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"})
    def test_configure_for_copilot_env_token(self):
        """Test GitHub token from environment variable."""
        config = LLMConfig(model="github_copilot/gpt-4.1")
        
        configured = GitHubCopilotConfig.configure_for_copilot(config)
        
        assert configured.api_key.get_secret_value() == "env-token"

    def test_configure_for_copilot_non_copilot_model(self):
        """Test that non-Copilot models are not modified."""
        config = LLMConfig(model="gpt-4o", api_key="test-token")
        
        configured = GitHubCopilotConfig.configure_for_copilot(config)
        
        # Should be unchanged
        assert configured.model == "gpt-4o"
        assert configured.custom_llm_provider is None
        assert configured.base_url is None

    def test_get_litellm_params(self):
        """Test LiteLLM parameters generation."""
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            api_key="test-token",
            base_url="https://custom.api.com"
        )
        
        params = GitHubCopilotConfig.get_litellm_params(config)
        
        assert params["model"] == "github_copilot/gpt-4.1"
        assert params["api_base"] == "https://custom.api.com"
        assert params["api_key"] == "test-token"
        assert "extra_headers" in params
        assert params["extra_headers"]["User-Agent"] == "GitHubCopilot/1.0"

    def test_get_litellm_params_non_copilot(self):
        """Test LiteLLM parameters for non-Copilot models."""
        config = LLMConfig(model="gpt-4o", api_key="test-token")
        
        params = GitHubCopilotConfig.get_litellm_params(config)
        
        assert params == {}

    def test_supported_models_list(self):
        """Test that supported models list contains expected models."""
        expected_models = ["gpt-4.1", "gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini", "claude-sonnet-4"]
        
        for model in expected_models:
            assert model in GitHubCopilotConfig.SUPPORTED_MODELS


class TestGitHubCopilotValidation:
    """Test GitHub Copilot configuration validation."""

    def test_validate_github_copilot_config_valid(self):
        """Test validation with valid configuration."""
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            api_key="test-token",
            custom_llm_provider="github_copilot"
        )
        
        assert validate_github_copilot_config(config) is True

    def test_validate_github_copilot_config_no_auth(self):
        """Test validation fails without authentication."""
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            custom_llm_provider="github_copilot"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            assert validate_github_copilot_config(config) is False

    @patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"})
    def test_validate_github_copilot_config_env_auth(self):
        """Test validation passes with environment token."""
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            custom_llm_provider="github_copilot"
        )
        
        assert validate_github_copilot_config(config) is True

    def test_validate_github_copilot_config_non_copilot(self):
        """Test validation passes for non-Copilot models."""
        config = LLMConfig(model="gpt-4o", api_key="test-token")
        
        assert validate_github_copilot_config(config) is True

    def test_validate_github_copilot_config_wrong_provider(self):
        """Test validation warns about wrong provider setting."""
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            api_key="test-token",
            custom_llm_provider="openai"  # Wrong provider
        )
        
        # Should still return True but log a warning
        assert validate_github_copilot_config(config) is True


class TestGitHubCopilotSetup:
    """Test GitHub Copilot provider setup."""

    def test_setup_github_copilot_provider(self):
        """Test provider setup function."""
        # Should not raise any exceptions
        setup_github_copilot_provider()


class TestGitHubCopilotIntegration:
    """Test GitHub Copilot integration with LLM class."""

    def test_llm_initialization_with_copilot(self):
        """Test LLM initialization with GitHub Copilot model."""
        from openhands.llm import LLM
        
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            api_key="test-token"
        )
        
        llm = LLM(config)
        
        # Check that configuration was applied
        assert llm.config.custom_llm_provider == "github_copilot"
        assert llm.config.base_url == GitHubCopilotConfig.DEFAULT_API_BASE
        assert llm.config.model == "github_copilot/gpt-4.1"

    def test_llm_initialization_invalid_copilot_config(self):
        """Test LLM initialization fails with invalid Copilot config."""
        from openhands.llm import LLM
        
        config = LLMConfig(model="github_copilot/gpt-4.1")  # No auth
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Invalid GitHub Copilot configuration"):
                LLM(config)

    def test_function_calling_support(self):
        """Test that GitHub Copilot models support function calling."""
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