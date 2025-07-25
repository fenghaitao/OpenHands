"""GitHub Copilot initialization command for OpenHands CLI."""

import asyncio
import click
from pathlib import Path

from openhands.core.config import load_openhands_config
from openhands.core.logger import openhands_logger as logger
from openhands.cli.github_copilot_setup import (
    setup_github_copilot_settings,
    detect_github_copilot_config,
    detect_github_copilot_mode,
)


@click.command()
@click.option(
    '--mode',
    type=click.Choice(['direct', 'proxy', 'auto']),
    default='auto',
    help='GitHub Copilot mode: direct, proxy, or auto-detect'
)
@click.option(
    '--file-store-path',
    type=click.Path(),
    help='Custom file store path (defaults to config file_store_path)'
)
@click.option(
    '--force',
    is_flag=True,
    help='Force overwrite existing settings.json'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be done without making changes'
)
def github_copilot_init(mode: str, file_store_path: str, force: bool, dry_run: bool):
    """Initialize GitHub Copilot settings for OpenHands.
    
    This command detects GitHub Copilot configuration and creates a settings.json
    file to avoid UI prompts for provider setup.
    """
    click.echo("🚀 GitHub Copilot Settings Initialization")
    click.echo("=" * 50)
    
    try:
        # Detect GitHub Copilot configuration
        copilot_config = detect_github_copilot_config()
        if not copilot_config:
            click.echo("❌ No GitHub Copilot configuration detected")
            click.echo("\nPlease ensure you have:")
            click.echo("  • A config.toml file with GitHub Copilot settings")
            click.echo("  • custom_llm_provider = 'github_copilot'")
            click.echo("  • A valid GitHub Copilot model (e.g., github_copilot/gpt-4.1)")
            click.echo("  • Authentication via OAuth or GITHUB_TOKEN")
            return
        
        # Determine mode
        if mode == 'auto':
            detected_mode = detect_github_copilot_mode()
            if detected_mode:
                mode = detected_mode
                click.echo(f"🔍 Auto-detected mode: {mode}")
            else:
                mode = 'direct'
                click.echo(f"🔍 Defaulting to mode: {mode}")
        else:
            click.echo(f"🔧 Using specified mode: {mode}")
        
        # Get file store path
        config = load_openhands_config()
        if not file_store_path:
            file_store_path = config.file_store_path
        
        file_store_path = Path(file_store_path).expanduser()
        settings_file = file_store_path / "settings.json"
        
        click.echo(f"📁 File store path: {file_store_path}")
        click.echo(f"📄 Settings file: {settings_file}")
        
        # Show configuration details
        click.echo("\n📋 Detected Configuration:")
        click.echo(f"  • Model: {copilot_config['model']}")
        click.echo(f"  • API Key Source: {copilot_config['api_key_source']}")
        click.echo(f"  • Base URL: {copilot_config.get('base_url', 'default')}")
        click.echo(f"  • Agent: {copilot_config.get('agent', 'CodeActAgent')}")
        
        # Check if settings already exist
        if settings_file.exists() and not force:
            click.echo(f"\n⚠️  Settings file already exists: {settings_file}")
            if not dry_run:
                if not click.confirm("Do you want to overwrite it?"):
                    click.echo("❌ Cancelled by user")
                    return
        
        if dry_run:
            click.echo("\n🔍 DRY RUN - No changes will be made")
            click.echo(f"Would create/update: {settings_file}")
            click.echo(f"Mode: {mode}")
            return
        
        # Setup settings
        async def setup():
            return await setup_github_copilot_settings(str(file_store_path), mode)
        
        success = asyncio.run(setup())
        
        if success:
            click.echo("\n✅ GitHub Copilot settings initialized successfully!")
            click.echo(f"📄 Settings saved to: {settings_file}")
            click.echo("\n🎉 You can now start OpenHands without provider setup prompts!")
        else:
            click.echo("\n❌ Failed to initialize GitHub Copilot settings")
            click.echo("Check the logs for more details")
            
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        logger.error(f"GitHub Copilot initialization failed: {e}")


if __name__ == '__main__':
    github_copilot_init()