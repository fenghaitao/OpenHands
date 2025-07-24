"""Authentication CLI commands for OpenHands.

This module provides CLI commands for authenticating with various services
like GitHub Copilot.
"""

import asyncio
import sys
from typing import Optional

import click

from openhands.core.logger import openhands_logger as logger


@click.group()
def auth():
    """Authentication commands for OpenHands services."""
    pass


@auth.command()
@click.option(
    '--timeout',
    default=900,
    help='Maximum time to wait for authentication (seconds)',
    type=int
)
@click.option(
    '--token-dir',
    default=None,
    help='Directory to store authentication tokens',
    type=str
)
@click.option(
    '--check-only',
    is_flag=True,
    help='Only check authentication status, do not authenticate'
)
@click.option(
    '--revoke',
    is_flag=True,
    help='Revoke existing authentication'
)
@click.option(
    '--status',
    is_flag=True,
    help='Show detailed authentication status'
)
def github_copilot(
    timeout: int,
    token_dir: Optional[str],
    check_only: bool,
    revoke: bool,
    status: bool
):
    """Authenticate with GitHub Copilot using OAuth device flow.
    
    This command will guide you through the GitHub OAuth process to authenticate
    with GitHub Copilot. You'll need to visit a URL and enter a code.
    
    Examples:
        openhands auth github-copilot                    # Start authentication
        openhands auth github-copilot --check-only      # Check if authenticated
        openhands auth github-copilot --status          # Show detailed status
        openhands auth github-copilot --revoke          # Revoke authentication
    """
    try:
        from openhands.llm.github_copilot_auth import (
            get_auth_manager,
            GitHubCopilotAuthenticationError
        )
    except ImportError as e:
        click.echo(f"❌ GitHub Copilot authentication not available: {e}", err=True)
        sys.exit(1)
    
    try:
        auth_manager = get_auth_manager(token_dir)
        
        # Handle revoke command
        if revoke:
            if auth_manager.is_authenticated():
                auth_manager.revoke_authentication()
                click.echo("✅ GitHub Copilot authentication revoked successfully")
            else:
                click.echo("ℹ️  No GitHub Copilot authentication to revoke")
            return
        
        # Handle status command
        if status:
            auth_status = auth_manager.get_auth_status()
            click.echo("📊 GitHub Copilot Authentication Status:")
            click.echo(f"   Authenticated: {'✅ Yes' if auth_status['authenticated'] else '❌ No'}")
            click.echo(f"   Token Directory: {auth_status['token_dir']}")
            click.echo(f"   Has Access Token: {'✅' if auth_status['has_access_token'] else '❌'}")
            click.echo(f"   Has API Key: {'✅' if auth_status['has_api_key'] else '❌'}")
            if auth_status['has_api_key']:
                click.echo(f"   API Key Expired: {'❌ Yes' if auth_status['api_key_expired'] else '✅ No'}")
            return
        
        # Handle check-only command
        if check_only:
            if auth_manager.is_authenticated():
                click.echo("✅ GitHub Copilot is authenticated and ready to use")
                sys.exit(0)
            else:
                click.echo("❌ GitHub Copilot is not authenticated")
                click.echo("💡 Run 'openhands auth github-copilot' to authenticate")
                sys.exit(1)
        
        # Perform authentication
        click.echo("🚀 Starting GitHub Copilot authentication...")
        
        if auth_manager.is_authenticated():
            click.echo("✅ Already authenticated with GitHub Copilot!")
            return
        
        success = auth_manager.authenticate(timeout)
        
        if success:
            click.echo("🎉 GitHub Copilot authentication completed successfully!")
            click.echo("💡 You can now use GitHub Copilot models in OpenHands")
        else:
            click.echo("❌ GitHub Copilot authentication failed")
            click.echo("💡 Please try again or check your internet connection")
            sys.exit(1)
            
    except GitHubCopilotAuthenticationError as e:
        click.echo(f"❌ Authentication error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n⏹️  Authentication cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@auth.command()
def list_providers():
    """List all available authentication providers."""
    click.echo("🔐 Available Authentication Providers:")
    click.echo("   • github-copilot  - GitHub Copilot OAuth authentication")
    click.echo("")
    click.echo("💡 Use 'openhands auth <provider> --help' for provider-specific options")


if __name__ == '__main__':
    auth()