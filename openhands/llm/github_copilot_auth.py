"""GitHub Copilot OAuth authentication manager for OpenHands.

This module provides OAuth authentication for GitHub Copilot by leveraging
LiteLLM's existing authenticator while providing a cleaner interface for OpenHands.
"""

import asyncio
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path

from openhands.core.logger import openhands_logger as logger

try:
    from litellm.llms.github_copilot.authenticator import Authenticator as LiteLLMAuthenticator
    from litellm.llms.github_copilot.common_utils import (
        GetAPIKeyError,
        GetAccessTokenError,
        GetDeviceCodeError,
    )
    LITELLM_AVAILABLE = True
except ImportError:
    logger.warning("LiteLLM GitHub Copilot authenticator not available")
    LITELLM_AVAILABLE = False
    LiteLLMAuthenticator = None
    GetAPIKeyError = Exception
    GetAccessTokenError = Exception
    GetDeviceCodeError = Exception


class GitHubCopilotAuthenticationError(Exception):
    """Exception raised when GitHub Copilot authentication fails."""
    pass


class GitHubCopilotAuthManager:
    """GitHub Copilot OAuth authentication manager for OpenHands.
    
    This class provides a high-level interface for GitHub Copilot authentication
    that integrates with OpenHands while leveraging LiteLLM's proven authenticator.
    """
    
    def __init__(self, token_dir: Optional[str] = None):
        """Initialize the authentication manager.
        
        Args:
            token_dir: Directory to store authentication tokens. 
                      Defaults to ~/.config/openhands/github_copilot
        """
        if not LITELLM_AVAILABLE:
            raise GitHubCopilotAuthenticationError(
                "LiteLLM GitHub Copilot authenticator is not available. "
                "Please ensure LiteLLM is properly installed."
            )
        
        # Set up token directory
        if token_dir is None:
            token_dir = os.path.expanduser("~/.config/openhands/github_copilot")
        
        self.token_dir = Path(token_dir)
        self.token_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure LiteLLM authenticator to use our token directory
        os.environ["GITHUB_COPILOT_TOKEN_DIR"] = str(self.token_dir)
        
        self._authenticator = LiteLLMAuthenticator()
        logger.debug(f"GitHub Copilot auth manager initialized with token dir: {self.token_dir}")
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated with GitHub Copilot.
        
        Returns:
            bool: True if authenticated and token is valid, False otherwise.
        """
        try:
            # Try to get a valid API key - this will check token expiration
            api_key = self._authenticator.get_api_key()
            return api_key is not None and len(api_key) > 0
        except (GetAPIKeyError, GetAccessTokenError, Exception) as e:
            logger.debug(f"Authentication check failed: {e}")
            return False
    
    def get_api_key(self) -> Optional[str]:
        """Get a valid GitHub Copilot API key.
        
        Returns:
            str: Valid API key if authenticated, None otherwise.
            
        Raises:
            GitHubCopilotAuthenticationError: If authentication fails.
        """
        try:
            return self._authenticator.get_api_key()
        except GetAPIKeyError as e:
            logger.error(f"Failed to get GitHub Copilot API key: {e}")
            raise GitHubCopilotAuthenticationError(f"Failed to get API key: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting API key: {e}")
            raise GitHubCopilotAuthenticationError(f"Unexpected error: {e}")
    
    def start_device_flow(self) -> Dict[str, Any]:
        """Start the OAuth device flow for authentication.
        
        Returns:
            dict: Device flow information containing:
                - device_code: Code for polling
                - user_code: Code for user to enter
                - verification_uri: URL for user to visit
                - expires_in: Expiration time in seconds
                - interval: Polling interval in seconds
                
        Raises:
            GitHubCopilotAuthenticationError: If device flow initiation fails.
        """
        try:
            # Use the internal method to get device code info
            device_info = self._authenticator._get_device_code()
            
            logger.info(
                f"GitHub Copilot device flow started. "
                f"Please visit {device_info['verification_uri']} "
                f"and enter code: {device_info['user_code']}"
            )
            
            return {
                'device_code': device_info['device_code'],
                'user_code': device_info['user_code'],
                'verification_uri': device_info['verification_uri'],
                'expires_in': device_info.get('expires_in', 900),  # Default 15 minutes
                'interval': device_info.get('interval', 5)  # Default 5 seconds
            }
        except GetDeviceCodeError as e:
            logger.error(f"Failed to start device flow: {e}")
            raise GitHubCopilotAuthenticationError(f"Failed to start device flow: {e}")
        except Exception as e:
            logger.error(f"Unexpected error starting device flow: {e}")
            raise GitHubCopilotAuthenticationError(f"Unexpected error: {e}")
    
    def poll_device_flow(self, device_code: str, timeout: int = 900) -> bool:
        """Poll for completion of the device flow.
        
        Args:
            device_code: Device code from start_device_flow()
            timeout: Maximum time to wait in seconds (default 15 minutes)
            
        Returns:
            bool: True if authentication successful, False if timeout/cancelled
            
        Raises:
            GitHubCopilotAuthenticationError: If polling fails with an error.
        """
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                try:
                    # Try to poll for access token
                    access_token = self._authenticator._poll_for_access_token(device_code)
                    if access_token:
                        logger.info("GitHub Copilot authentication successful!")
                        return True
                except GetAccessTokenError as e:
                    # Check if it's a timeout or authorization pending
                    if "authorization_pending" in str(e).lower():
                        time.sleep(5)  # Wait before next poll
                        continue
                    elif "timeout" in str(e).lower() or "expired" in str(e).lower():
                        logger.warning("Device flow expired or timed out")
                        return False
                    else:
                        # Other error, re-raise
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error during polling: {e}")
                    raise GitHubCopilotAuthenticationError(f"Polling failed: {e}")
            
            logger.warning("Device flow polling timed out")
            return False
            
        except GitHubCopilotAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during device flow polling: {e}")
            raise GitHubCopilotAuthenticationError(f"Polling failed: {e}")
    
    async def authenticate_async(self, timeout: int = 900) -> bool:
        """Perform complete OAuth authentication flow asynchronously.
        
        Args:
            timeout: Maximum time to wait for user authentication
            
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            GitHubCopilotAuthenticationError: If authentication process fails.
        """
        # Check if already authenticated
        if self.is_authenticated():
            logger.info("Already authenticated with GitHub Copilot")
            return True
        
        # Start device flow
        device_info = self.start_device_flow()
        
        # Print instructions for user
        print(f"\n🔐 GitHub Copilot Authentication Required")
        print(f"📱 Please visit: {device_info['verification_uri']}")
        print(f"🔑 Enter code: {device_info['user_code']}")
        print(f"⏱️  Code expires in {device_info['expires_in'] // 60} minutes")
        print(f"⏳ Waiting for authentication...\n")
        
        # Poll for completion in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None, 
            self.poll_device_flow, 
            device_info['device_code'], 
            timeout
        )
        
        if success:
            print("✅ GitHub Copilot authentication successful!")
        else:
            print("❌ GitHub Copilot authentication failed or timed out")
        
        return success
    
    def authenticate(self, timeout: int = 900) -> bool:
        """Perform complete OAuth authentication flow synchronously.
        
        Args:
            timeout: Maximum time to wait for user authentication
            
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            GitHubCopilotAuthenticationError: If authentication process fails.
        """
        # Check if already authenticated
        if self.is_authenticated():
            logger.info("Already authenticated with GitHub Copilot")
            return True
        
        # Start device flow
        device_info = self.start_device_flow()
        
        # Print instructions for user
        print(f"\n🔐 GitHub Copilot Authentication Required")
        print(f"📱 Please visit: {device_info['verification_uri']}")
        print(f"🔑 Enter code: {device_info['user_code']}")
        print(f"⏱️  Code expires in {device_info['expires_in'] // 60} minutes")
        print(f"⏳ Waiting for authentication...\n")
        
        # Poll for completion
        success = self.poll_device_flow(device_info['device_code'], timeout)
        
        if success:
            print("✅ GitHub Copilot authentication successful!")
        else:
            print("❌ GitHub Copilot authentication failed or timed out")
        
        return success
    
    def revoke_authentication(self) -> None:
        """Revoke authentication by removing stored tokens.
        
        This will require the user to re-authenticate on next use.
        """
        try:
            # Remove token files
            access_token_file = self.token_dir / "access-token"
            api_key_file = self.token_dir / "api-key.json"
            
            if access_token_file.exists():
                access_token_file.unlink()
                logger.debug("Removed access token file")
            
            if api_key_file.exists():
                api_key_file.unlink()
                logger.debug("Removed API key file")
            
            logger.info("GitHub Copilot authentication revoked")
            
        except Exception as e:
            logger.error(f"Error revoking authentication: {e}")
            raise GitHubCopilotAuthenticationError(f"Failed to revoke authentication: {e}")
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get detailed authentication status information.
        
        Returns:
            dict: Authentication status containing:
                - authenticated: bool
                - token_dir: str
                - has_access_token: bool
                - has_api_key: bool
                - api_key_expired: bool (if applicable)
        """
        access_token_file = self.token_dir / "access-token"
        api_key_file = self.token_dir / "api-key.json"
        
        status = {
            'authenticated': self.is_authenticated(),
            'token_dir': str(self.token_dir),
            'has_access_token': access_token_file.exists(),
            'has_api_key': api_key_file.exists(),
            'api_key_expired': False
        }
        
        # Check API key expiration if file exists
        if api_key_file.exists():
            try:
                import json
                with open(api_key_file, 'r') as f:
                    api_key_info = json.load(f)
                    expires_at = api_key_info.get('expires_at', 0)
                    status['api_key_expired'] = expires_at <= time.time()
            except Exception:
                status['api_key_expired'] = True
        
        return status


# Global instance for easy access
_auth_manager: Optional[GitHubCopilotAuthManager] = None


def get_auth_manager(token_dir: Optional[str] = None) -> GitHubCopilotAuthManager:
    """Get the global GitHub Copilot authentication manager instance.
    
    Args:
        token_dir: Token directory (only used on first call)
        
    Returns:
        GitHubCopilotAuthManager: The authentication manager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = GitHubCopilotAuthManager(token_dir)
    return _auth_manager


def is_authenticated() -> bool:
    """Check if GitHub Copilot is authenticated (convenience function).
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    try:
        return get_auth_manager().is_authenticated()
    except GitHubCopilotAuthenticationError:
        return False


def authenticate(timeout: int = 900) -> bool:
    """Authenticate with GitHub Copilot (convenience function).
    
    Args:
        timeout: Maximum time to wait for authentication
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        return get_auth_manager().authenticate(timeout)
    except GitHubCopilotAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        return False


# Export main classes and functions
__all__ = [
    'GitHubCopilotAuthManager',
    'GitHubCopilotAuthenticationError',
    'get_auth_manager',
    'is_authenticated',
    'authenticate'
]