#!/usr/bin/env python3
"""Live integration test for GitHub Copilot OAuth provider.

This script provides a comprehensive test of the GitHub Copilot integration
with real authentication and API calls. Use this to validate the complete
OAuth flow and LLM functionality.

Usage:
    python tests/integration/test_github_copilot_live.py
    
Environment Variables:
    GITHUB_TOKEN - GitHub token for fallback authentication
    GITHUB_COPILOT_LIVE_TEST - Set to '1' to enable live API calls
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openhands.core.config import LLMConfig
from openhands.llm import LLM
from openhands.llm.github_copilot_auth import (
    GitHubCopilotAuthManager,
    GitHubCopilotAuthenticationError,
)
from openhands.llm.github_copilot import GitHubCopilotConfig, validate_github_copilot_config


class GitHubCopilotLiveTest:
    """Live integration test for GitHub Copilot."""
    
    def __init__(self):
        self.auth_manager = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, message))
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
    
    def print_summary(self):
        """Print test summary."""
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"\n📊 Test Summary: {passed}/{total} tests passed")
        
        if passed < total:
            print("\n❌ Failed tests:")
            for name, success, message in self.test_results:
                if not success:
                    print(f"  • {name}: {message}")
        
        return passed == total
    
    def test_authentication_manager_initialization(self):
        """Test authentication manager initialization."""
        try:
            self.auth_manager = GitHubCopilotAuthManager()
            self.log_test("Authentication Manager Initialization", True)
            return True
        except Exception as e:
            self.log_test("Authentication Manager Initialization", False, str(e))
            return False
    
    def test_authentication_status(self):
        """Test authentication status checking."""
        try:
            if not self.auth_manager:
                self.log_test("Authentication Status Check", False, "Auth manager not initialized")
                return False
            
            is_authenticated = self.auth_manager.is_authenticated()
            status = self.auth_manager.get_auth_status()
            
            self.log_test("Authentication Status Check", True, 
                         f"Authenticated: {is_authenticated}, Status: {status['authenticated']}")
            return True
        except Exception as e:
            self.log_test("Authentication Status Check", False, str(e))
            return False
    
    async def test_oauth_flow(self):
        """Test OAuth authentication flow (interactive)."""
        try:
            if not self.auth_manager:
                self.log_test("OAuth Flow Test", False, "Auth manager not initialized")
                return False
            
            if self.auth_manager.is_authenticated():
                self.log_test("OAuth Flow Test", True, "Already authenticated")
                return True
            
            print("\n🔐 Starting OAuth authentication flow...")
            print("This will open a browser window for GitHub authentication.")
            
            user_input = input("Continue with OAuth test? (y/N): ").strip().lower()
            if user_input != 'y':
                self.log_test("OAuth Flow Test", True, "Skipped by user")
                return True
            
            success = await self.auth_manager.authenticate_async(timeout=300)  # 5 minutes
            self.log_test("OAuth Flow Test", success, 
                         "Authentication completed" if success else "Authentication failed")
            return success
            
        except Exception as e:
            self.log_test("OAuth Flow Test", False, str(e))
            return False
    
    def test_token_retrieval(self):
        """Test API token retrieval."""
        try:
            if not self.auth_manager:
                self.log_test("Token Retrieval", False, "Auth manager not initialized")
                return False
            
            if not self.auth_manager.is_authenticated():
                # Try environment variable fallback
                github_token = os.getenv("GITHUB_TOKEN")
                if github_token:
                    self.log_test("Token Retrieval", True, "Using GITHUB_TOKEN environment variable")
                    return True
                else:
                    self.log_test("Token Retrieval", False, "Not authenticated and no GITHUB_TOKEN")
                    return False
            
            api_key = self.auth_manager.get_api_key()
            success = api_key is not None and len(api_key) > 0
            
            self.log_test("Token Retrieval", success, 
                         f"Token length: {len(api_key) if api_key else 0}")
            return success
            
        except Exception as e:
            self.log_test("Token Retrieval", False, str(e))
            return False
    
    def test_llm_configuration(self):
        """Test LLM configuration with GitHub Copilot."""
        try:
            config = LLMConfig(model="github_copilot/gpt-4.1")
            
            # Test model detection
            is_copilot = GitHubCopilotConfig.is_github_copilot_model(config.model)
            if not is_copilot:
                self.log_test("LLM Configuration", False, "Model not detected as GitHub Copilot")
                return False
            
            # Test configuration
            configured = GitHubCopilotConfig.configure_for_copilot(config)
            
            # Test validation
            is_valid = validate_github_copilot_config(configured)
            
            self.log_test("LLM Configuration", is_valid,
                         f"Provider: {configured.custom_llm_provider}, "
                         f"Base URL: {configured.base_url}, "
                         f"Has API key: {configured.api_key is not None}")
            return is_valid
            
        except Exception as e:
            self.log_test("LLM Configuration", False, str(e))
            return False
    
    def test_llm_initialization(self):
        """Test LLM initialization with GitHub Copilot."""
        try:
            config = LLMConfig(
                model="github_copilot/gpt-4.1",
                temperature=0.1,
                max_output_tokens=100
            )
            
            llm = LLM(config)
            
            success = (
                llm.config.custom_llm_provider == "github_copilot" and
                llm.config.base_url == GitHubCopilotConfig.DEFAULT_API_BASE and
                llm.config.api_key is not None
            )
            
            self.log_test("LLM Initialization", success,
                         f"Model: {llm.config.model}, Provider: {llm.config.custom_llm_provider}")
            return success
            
        except Exception as e:
            self.log_test("LLM Initialization", False, str(e))
            return False
    
    def test_live_completion(self):
        """Test live completion with GitHub Copilot (if enabled)."""
        if not os.getenv("GITHUB_COPILOT_LIVE_TEST"):
            self.log_test("Live Completion Test", True, "Skipped (set GITHUB_COPILOT_LIVE_TEST=1 to enable)")
            return True
        
        try:
            config = LLMConfig(
                model="github_copilot/gpt-4.1",
                temperature=0.1,
                max_output_tokens=150
            )
            
            llm = LLM(config)
            
            messages = [
                {
                    "role": "user", 
                    "content": "Write a simple Python function that calculates the factorial of a number."
                }
            ]
            
            print("\n🤖 Making live API call to GitHub Copilot...")
            response = llm.completion(messages=messages)
            
            success = (
                response is not None and
                response.choices is not None and
                len(response.choices) > 0 and
                response.choices[0].message.content is not None
            )
            
            if success:
                content = response.choices[0].message.content
                self.log_test("Live Completion Test", True, 
                             f"Response length: {len(content)} chars")
                print(f"\n📝 Response preview:\n{content[:200]}{'...' if len(content) > 200 else ''}")
            else:
                self.log_test("Live Completion Test", False, "No valid response received")
            
            return success
            
        except Exception as e:
            self.log_test("Live Completion Test", False, str(e))
            return False
    
    def test_multiple_models(self):
        """Test multiple GitHub Copilot models."""
        models_to_test = [
            "github_copilot/gpt-4.1",
            "github_copilot/gpt-4o-mini",
        ]
        
        success_count = 0
        
        for model in models_to_test:
            try:
                config = LLMConfig(model=model)
                configured = GitHubCopilotConfig.configure_for_copilot(config)
                
                if validate_github_copilot_config(configured):
                    llm = LLM(configured)
                    success_count += 1
                    print(f"  ✅ {model}")
                else:
                    print(f"  ❌ {model} - Configuration validation failed")
                    
            except Exception as e:
                print(f"  ❌ {model} - {str(e)}")
        
        success = success_count == len(models_to_test)
        self.log_test("Multiple Models Test", success, 
                     f"{success_count}/{len(models_to_test)} models configured successfully")
        return success
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🚀 GitHub Copilot Live Integration Test")
        print("=" * 50)
        
        # Basic tests
        if not self.test_authentication_manager_initialization():
            return False
        
        self.test_authentication_status()
        
        # OAuth test (interactive)
        await self.test_oauth_flow()
        
        # Token and configuration tests
        self.test_token_retrieval()
        self.test_llm_configuration()
        self.test_llm_initialization()
        self.test_multiple_models()
        
        # Live API test (optional)
        self.test_live_completion()
        
        return self.print_summary()


async def main():
    """Main test function."""
    print("GitHub Copilot Live Integration Test")
    print("This test validates the complete GitHub Copilot OAuth integration.")
    print()
    
    # Check environment
    if os.getenv("GITHUB_COPILOT_LIVE_TEST"):
        print("🔴 Live API testing enabled (GITHUB_COPILOT_LIVE_TEST=1)")
    else:
        print("🟡 Live API testing disabled (set GITHUB_COPILOT_LIVE_TEST=1 to enable)")
    
    if os.getenv("GITHUB_TOKEN"):
        print("🟢 GITHUB_TOKEN environment variable available")
    else:
        print("🟡 No GITHUB_TOKEN environment variable (OAuth will be required)")
    
    print()
    
    # Run tests
    test_runner = GitHubCopilotLiveTest()
    success = await test_runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! GitHub Copilot integration is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the configuration and authentication.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
