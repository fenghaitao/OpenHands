"""GitHub Copilot setup utilities for OpenHands.

This module provides functionality to pre-populate settings.json with GitHub Copilot
configuration to avoid UI prompts for provider setup.
"""

import os
import json
from pathlib import Path
from typing import Optional

from pydantic import SecretStr

from openhands.core.config import load_openhands_config
from openhands.core.logger import openhands_logger as logger
from openhands.llm.github_copilot import GitHubCopilotConfig
from openhands.llm.github_copilot_auth import get_auth_manager, is_authenticated
from openhands.storage.data_models.settings import Settings
from openhands.storage.settings.file_settings_store import FileSettingsStore
from openhands.storage import get_file_store


def detect_github_copilot_config(config_file: str = 'config.toml') -> Optional[dict]:
    """Detect GitHub Copilot configuration from config files and environment.
    
    Args:
        config_file: Path to the config file (default: config.toml)
    
    Returns:
        Dictionary with GitHub Copilot settings if detected, None otherwise.
    """
    try:
        config = load_openhands_config(config_file=config_file)
        llm_config = config.get_llm_config()
        
        # Check if this is a GitHub Copilot configuration
        # Support both direct github_copilot models and proxy mode
        is_github_copilot_proxy = llm_config.model and llm_config.model.startswith('litellm_proxy/github_copilot/')
        is_github_copilot_direct = llm_config.custom_llm_provider == "github_copilot"
        
        if not (is_github_copilot_proxy or is_github_copilot_direct):
            return None
            
        logger.info(f"Detected GitHub Copilot configuration: {llm_config.model}")
        
        # Determine API key source
        api_key = None
        api_key_source = "none"
        
        # Check OAuth authentication first
        try:
            if is_authenticated():
                auth_manager = get_auth_manager()
                oauth_key = auth_manager.get_api_key()
                if oauth_key:
                    api_key = oauth_key
                    api_key_source = "oauth"
                    logger.debug("Using OAuth token for GitHub Copilot")
        except Exception as e:
            logger.debug(f"OAuth authentication check failed: {e}")
        
        # Check environment variable
        if not api_key:
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                api_key = github_token
                api_key_source = "environment"
                logger.debug("Using GITHUB_TOKEN environment variable")
        
        # Check config file API key
        if not api_key and llm_config.api_key:
            api_key = llm_config.api_key.get_secret_value()
            api_key_source = "config"
            logger.debug("Using API key from config file")
        
        if not api_key:
            logger.warning("No GitHub Copilot API key found")
            return None
            
        return {
            "model": llm_config.model,
            "api_key": api_key,
            "api_key_source": api_key_source,
            "base_url": llm_config.base_url,
            "custom_llm_provider": "github_copilot",
            "agent": config.default_agent,
            "max_iterations": config.max_iterations,
        }
        
    except Exception as e:
        logger.debug(f"Failed to detect GitHub Copilot configuration: {e}")
        return None


def create_github_copilot_settings(copilot_config: dict, mode: str = "direct") -> Settings:
    """Create Settings object for GitHub Copilot.
    
    Args:
        copilot_config: GitHub Copilot configuration dictionary
        mode: Either "direct" or "proxy" mode
        
    Returns:
        Settings object configured for GitHub Copilot
    """
    # Use original model name from config without modification
    model = copilot_config["model"]
    
    settings = Settings(
        language="en",
        agent=copilot_config.get("agent", "CodeActAgent"),
        max_iterations=copilot_config.get("max_iterations", 100),
        security_analyzer=None,
        confirmation_mode=True,
        llm_model=model,
        llm_api_key=SecretStr(copilot_config["api_key"]),
        llm_base_url=copilot_config.get("base_url"),
        enable_default_condenser=True,
        enable_sound_notifications=False,
        enable_proactive_conversation_starters=True,
    )
    
    return settings


async def setup_github_copilot_settings(file_store_path: Optional[str] = None, mode: str = "direct", config_file: str = 'config.toml') -> bool:
    """Set up GitHub Copilot settings.json file.
    
    Args:
        file_store_path: Path to file store directory. If None, uses default from config.
        mode: Either "direct" or "proxy" mode
        config_file: Path to the config file (default: config.toml)
        
    Returns:
        True if settings were created/updated, False otherwise
    """
    try:
        # Detect GitHub Copilot configuration
        copilot_config = detect_github_copilot_config(config_file)
        if not copilot_config:
            logger.info("No GitHub Copilot configuration detected")
            return False
        
        # Load OpenHands config to get file store path
        config = load_openhands_config(config_file=config_file)
        if file_store_path is None:
            file_store_path = config.file_store_path
        
        # Expand user path
        file_store_path = os.path.expanduser(file_store_path)
        
        # Create file store
        file_store = get_file_store(
            config.file_store,
            file_store_path,
            config.file_store_web_hook_url,
            config.file_store_web_hook_headers,
        )
        
        # Create settings store
        settings_store = FileSettingsStore(file_store)
        
        # Check if settings already exist
        existing_settings = await settings_store.load()
        if existing_settings and existing_settings.llm_model:
            logger.info(f"Settings already exist with model: {existing_settings.llm_model}")
            # Check if it's already a GitHub Copilot model
            if GitHubCopilotConfig.is_github_copilot_model(existing_settings.llm_model):
                logger.info("GitHub Copilot settings already configured")
                return False
        
        # Create new settings
        settings = create_github_copilot_settings(copilot_config, mode)
        
        # Store settings
        await settings_store.store(settings)
        
        settings_file_path = Path(file_store_path) / "settings.json"
        logger.info(f"✅ GitHub Copilot settings created at: {settings_file_path}")
        logger.info(f"   Model: {settings.llm_model}")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   API Key Source: {copilot_config['api_key_source']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup GitHub Copilot settings: {e}")
        return False


def setup_github_copilot_settings_sync(file_store_path: Optional[str] = None, mode: str = "direct", config_file: str = 'config.toml') -> bool:
    """Synchronous wrapper for setup_github_copilot_settings."""
    import asyncio
    
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a new task
            task = asyncio.create_task(setup_github_copilot_settings(file_store_path, mode, config_file))
            # We can't await in a running loop, so we return False and log a warning
            logger.warning("Event loop is running, cannot setup GitHub Copilot settings synchronously")
            return False
        else:
            return loop.run_until_complete(setup_github_copilot_settings(file_store_path, mode, config_file))
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(setup_github_copilot_settings(file_store_path, mode, config_file))


def detect_github_copilot_mode(config_file: str = 'config.toml') -> Optional[str]:
    """Detect GitHub Copilot mode from configuration.
    
    Args:
        config_file: Path to the config file (default: config.toml)
    
    Returns:
        "direct", "proxy", or None if not GitHub Copilot
    """
    try:
        config = load_openhands_config(config_file=config_file)
        llm_config = config.get_llm_config()
        
        if not GitHubCopilotConfig.is_github_copilot_model(llm_config.model):
            return None
            
        # Check if using proxy mode based on model name
        if llm_config.model.startswith("litellm_proxy/github_copilot/"):
            return "proxy"
        else:
            return "direct"
            
    except Exception:
        return None
