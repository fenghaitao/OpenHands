"""GitHub Copilot LLM provider for OpenHands.

This module provides integration with GitHub Copilot's API through LiteLLM.
GitHub Copilot uses a custom authentication and API format that requires
specific headers and configuration.
"""

import os
import asyncio
from typing import Any, Dict, Optional

from pydantic import SecretStr
from openhands.core.config import LLMConfig
from openhands.core.logger import openhands_logger as logger
from openhands.llm.github_copilot_auth import (
    GitHubCopilotAuthManager,
    GitHubCopilotAuthenticationError,
    get_auth_manager,
    is_authenticated,
)


class GitHubCopilotConfig:
    """Configuration helper for GitHub Copilot provider."""
    
    # Default GitHub Copilot API configuration
    DEFAULT_API_BASE = "https://api.githubcopilot.com"
    DEFAULT_HEADERS = {
        "Editor-Version": "vscode/1.85.0",
        "Editor-Plugin-Version": "copilot-chat/0.11.1", 
        "User-Agent": "GitHubCopilot/1.0",
        "Copilot-Integration-Id": "vscode-chat"
    }
    
    # Supported GitHub Copilot models
    SUPPORTED_MODELS = [
        "gpt-4.1",
        "gpt-4o",
        "gpt-4o-mini",
        "o1-preview",
        "o1-mini",
        "claude-sonnet-4"
    ]

    @classmethod
    def is_github_copilot_model(cls, model: str) -> bool:
        """Check if the model is a GitHub Copilot model."""
        return (
            model.startswith("github_copilot/") or
            model.startswith("copilot/") or
            model in [f"github_copilot/{m}" for m in cls.SUPPORTED_MODELS]
        )

    @classmethod
    def get_copilot_model_name(cls, model: str) -> str:
        """Extract the actual model name from GitHub Copilot model string."""
        if model.startswith("github_copilot/"):
            return model.removeprefix("github_copilot/")
        elif model.startswith("copilot/"):
            return model.removeprefix("copilot/")
        return model

    @classmethod
    def configure_for_copilot(cls, config: LLMConfig) -> LLMConfig:
        """Configure LLMConfig for GitHub Copilot usage."""
        if not cls.is_github_copilot_model(config.model):
            return config
            
        # Extract the actual model name
        actual_model = cls.get_copilot_model_name(config.model)
        
        # Ensure the model is supported
        if actual_model not in cls.SUPPORTED_MODELS:
            logger.warning(
                f"Model {actual_model} may not be supported by GitHub Copilot. "
                f"Supported models: {cls.SUPPORTED_MODELS}"
            )
        
        # Set GitHub Copilot specific configuration
        config.custom_llm_provider = "github_copilot"
        config.base_url = cls.DEFAULT_API_BASE
        
        # Ensure the model format is correct for LiteLLM
        if not config.model.startswith("github_copilot/"):
            config.model = f"github_copilot/{actual_model}"
            
        # Handle authentication with OAuth or fallback to environment variable
        if not config.api_key:
            # Try OAuth authentication first
            try:
                auth_manager = get_auth_manager()
                if auth_manager.is_authenticated():
                    api_key = auth_manager.get_api_key()
                    if api_key:
                        config.api_key = SecretStr(api_key)
                        logger.debug("Using OAuth token for GitHub Copilot authentication")
                    else:
                        logger.warning("OAuth authenticated but failed to get API key")
                else:
                    logger.info("GitHub Copilot OAuth not authenticated, checking environment variable")
            except (GitHubCopilotAuthenticationError, Exception) as e:
                logger.debug(f"OAuth authentication not available: {e}")
            
            # Fallback to environment variable if OAuth not available
            if not config.api_key:
                github_token = os.getenv("GITHUB_TOKEN")
                if github_token:
                    config.api_key = SecretStr(github_token)
                    logger.debug("Using GITHUB_TOKEN for GitHub Copilot authentication")
                else:
                    logger.warning(
                        "No API key provided for GitHub Copilot. "
                        "Use 'openhands auth github-copilot' to authenticate or "
                        "set GITHUB_TOKEN environment variable."
                    )
        
        logger.info(f"Configured GitHub Copilot with model: {config.model}")
        return config

    @classmethod
    def get_litellm_params(cls, config: LLMConfig) -> Dict[str, Any]:
        """Get LiteLLM parameters for GitHub Copilot."""
        if not cls.is_github_copilot_model(config.model):
            return {}
            
        params = {
            "model": config.model,
            "api_base": config.base_url or cls.DEFAULT_API_BASE,
            "api_key": config.api_key.get_secret_value() if config.api_key else None,
            "extra_headers": cls.DEFAULT_HEADERS.copy()
        }
        
        # Add custom headers if needed
        if hasattr(config, 'extra_headers') and config.extra_headers:
            params["extra_headers"].update(config.extra_headers)
            
        return params


def setup_github_copilot_provider() -> None:
    """Set up GitHub Copilot provider configuration."""
    # This function can be called during initialization to ensure
    # GitHub Copilot is properly configured
    logger.debug("GitHub Copilot provider setup completed")


def validate_github_copilot_config(config: LLMConfig) -> bool:
    """Validate GitHub Copilot configuration."""
    if not GitHubCopilotConfig.is_github_copilot_model(config.model):
        return True  # Not a Copilot model, validation passes
    
    # Check if we have authentication through OAuth or environment variable
    has_auth = False
    
    if config.api_key:
        has_auth = True
    else:
        # Check OAuth authentication
        try:
            if is_authenticated():
                has_auth = True
                logger.debug("GitHub Copilot OAuth authentication available")
        except GitHubCopilotAuthenticationError:
            pass
        
        # Check environment variable
        if not has_auth and os.getenv("GITHUB_TOKEN"):
            has_auth = True
            logger.debug("GITHUB_TOKEN environment variable available")
    
    if not has_auth:
        logger.error(
            "GitHub Copilot requires authentication. "
            "Use 'openhands auth github-copilot' to authenticate or "
            "set GITHUB_TOKEN environment variable."
        )
        return False
        
    if config.custom_llm_provider != "github_copilot":
        logger.warning(
            "GitHub Copilot model detected but custom_llm_provider is not set to 'github_copilot'. "
            "This may cause authentication issues."
        )
        
    return True


# Export the main configuration class and utility functions
__all__ = [
    "GitHubCopilotConfig",
    "setup_github_copilot_provider", 
    "validate_github_copilot_config"
]