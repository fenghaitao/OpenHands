"""GitHub Copilot startup utilities for OpenHands server.

This module provides functionality to pre-populate settings.json with GitHub Copilot
configuration during server startup to avoid UI prompts for provider setup.
"""

import asyncio
from typing import Optional

from openhands.core.config import load_openhands_config
from openhands.core.logger import openhands_logger as logger
from openhands.cli.github_copilot_setup import (
    setup_github_copilot_settings,
    detect_github_copilot_mode,
)


async def auto_setup_github_copilot_on_startup(user_id: Optional[str] = None, config_file: str = 'config.toml') -> bool:
    """Auto-setup GitHub Copilot settings during server startup.
    
    This function checks if GitHub Copilot is configured and automatically
    creates settings.json to avoid UI prompts for provider setup.
    
    Args:
        user_id: User ID for multi-user setups (currently unused)
        config_file: Path to the config file (default: config.toml)
        
    Returns:
        True if settings were created/updated, False otherwise
    """
    try:
        # Detect GitHub Copilot mode
        mode = detect_github_copilot_mode(config_file)
        if not mode:
            logger.debug("No GitHub Copilot configuration detected")
            return False
        
        logger.info(f"Detected GitHub Copilot configuration in {mode} mode")
        
        # Load config to get file store path
        config = load_openhands_config(config_file=config_file)
        
        # Setup GitHub Copilot settings
        success = await setup_github_copilot_settings(config.file_store_path, mode, config_file)
        
        if success:
            logger.info("✅ GitHub Copilot settings auto-configured for server startup")
        else:
            logger.debug("GitHub Copilot settings already exist or setup failed")
            
        return success
        
    except Exception as e:
        logger.warning(f"Failed to auto-setup GitHub Copilot settings: {e}")
        return False


def setup_github_copilot_on_startup_sync(user_id: Optional[str] = None, config_file: str = 'config.toml') -> bool:
    """Synchronous wrapper for auto_setup_github_copilot_on_startup."""
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, schedule the task
            task = asyncio.create_task(auto_setup_github_copilot_on_startup(user_id, config_file))
            logger.debug("Scheduled GitHub Copilot auto-setup task")
            return False  # Can't wait for result in running loop
        else:
            return loop.run_until_complete(auto_setup_github_copilot_on_startup(user_id, config_file))
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(auto_setup_github_copilot_on_startup(user_id, config_file))