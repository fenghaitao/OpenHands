#!/usr/bin/env python3
"""
Example demonstrating GitHub Copilot OAuth authentication and usage with OpenHands.

This example shows:
1. How to authenticate with GitHub Copilot using OAuth
2. How to configure OpenHands to use GitHub Copilot models
3. How to make LLM calls with GitHub Copilot
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openhands.core.config import LLMConfig
from openhands.llm import LLM
from openhands.llm.github_copilot_auth import (
    GitHubCopilotAuthManager,
    GitHubCopilotAuthenticationError,
)


async def authenticate_github_copilot():
    """Authenticate with GitHub Copilot using OAuth device flow."""
    print("🔐 GitHub Copilot Authentication Example")
    print("=" * 50)
    
    try:
        # Initialize the authentication manager
        auth_manager = GitHubCopilotAuthManager()
        
        # Check if already authenticated
        if auth_manager.is_authenticated():
            print("✅ Already authenticated with GitHub Copilot!")
            return True
        
        print("🚀 Starting GitHub Copilot OAuth authentication...")
        
        # Start the authentication flow
        success = await auth_manager.authenticate_async(timeout=900)  # 15 minutes
        
        if success:
            print("🎉 Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except GitHubCopilotAuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_github_copilot_llm():
    """Test GitHub Copilot LLM integration."""
    print("\n🤖 Testing GitHub Copilot LLM Integration")
    print("=" * 50)
    
    try:
        # Configure LLM for GitHub Copilot
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            temperature=0.1,
            max_output_tokens=1000
        )
        
        print(f"📝 Model: {config.model}")
        print(f"🌡️  Temperature: {config.temperature}")
        print(f"🔢 Max tokens: {config.max_output_tokens}")
        
        # Initialize LLM
        llm = LLM(config)
        
        print(f"✅ LLM initialized successfully")
        print(f"🔧 Provider: {llm.config.custom_llm_provider}")
        print(f"🌐 Base URL: {llm.config.base_url}")
        print(f"🔑 Has API key: {'Yes' if llm.config.api_key else 'No'}")
        
        # Test a simple completion
        print("\n💭 Testing completion...")
        messages = [
            {
                "role": "user", 
                "content": "Write a simple Python function to calculate the factorial of a number."
            }
        ]
        
        response = llm.completion(messages=messages)
        
        if response and response.choices:
            content = response.choices[0].message.content
            print("📤 Response received:")
            print("-" * 30)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 30)
            print("✅ GitHub Copilot LLM test successful!")
        else:
            print("❌ No response received")
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False
    
    return True


def show_auth_status():
    """Show detailed authentication status."""
    print("\n📊 Authentication Status")
    print("=" * 50)
    
    try:
        auth_manager = GitHubCopilotAuthManager()
        status = auth_manager.get_auth_status()
        
        print(f"Authenticated: {'✅ Yes' if status['authenticated'] else '❌ No'}")
        print(f"Token Directory: {status['token_dir']}")
        print(f"Has Access Token: {'✅' if status['has_access_token'] else '❌'}")
        print(f"Has API Key: {'✅' if status['has_api_key'] else '❌'}")
        
        if status['has_api_key']:
            print(f"API Key Expired: {'❌ Yes' if status['api_key_expired'] else '✅ No'}")
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")


def main():
    """Main example function."""
    print("🚀 OpenHands GitHub Copilot OAuth Example")
    print("=" * 60)
    
    # Show initial status
    show_auth_status()
    
    # Check if we need to authenticate
    try:
        auth_manager = GitHubCopilotAuthManager()
        if not auth_manager.is_authenticated():
            print("\n🔐 Authentication required...")
            success = asyncio.run(authenticate_github_copilot())
            if not success:
                print("❌ Cannot proceed without authentication")
                return
        else:
            print("\n✅ Already authenticated!")
    except Exception as e:
        print(f"❌ Authentication check failed: {e}")
        return
    
    # Show updated status
    show_auth_status()
    
    # Test LLM integration
    test_github_copilot_llm()
    
    print("\n🎉 Example completed!")
    print("\n💡 You can now use GitHub Copilot models in OpenHands:")
    print("   openhands --model github_copilot/gpt-4.1")


if __name__ == "__main__":
    main()