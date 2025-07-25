#!/usr/bin/env python3
"""
GitHub Copilot Provider Validation Script

This script validates the GitHub Copilot OAuth provider integration with OpenHands.
It tests authentication, configuration, and basic LLM functionality.

Usage:
    python validate_github_copilot.py [--live-test] [--model MODEL_NAME]

Examples:
    python validate_github_copilot.py
    python validate_github_copilot.py --live-test
    python validate_github_copilot.py --model github_copilot/claude-sonnet-4
"""

import argparse
import os
import sys
from typing import Optional

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from openhands.core.config import LLMConfig
        from openhands.llm import LLM
        from openhands.llm.github_copilot import GitHubCopilotConfig, validate_github_copilot_config
        from openhands.llm.github_copilot_auth import GitHubCopilotAuthManager
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_model_detection():
    """Test GitHub Copilot model detection."""
    print("\n🔍 Testing model detection...")
    try:
        from openhands.llm.github_copilot import GitHubCopilotConfig
        
        # Test positive cases
        test_models = [
            "github_copilot/gpt-4.1",
            "github_copilot/claude-sonnet-4",
            "copilot/gpt-4o"
        ]
        
        for model in test_models:
            if not GitHubCopilotConfig.is_github_copilot_model(model):
                print(f"  ❌ Failed to detect {model} as GitHub Copilot model")
                return False
        
        # Test negative cases
        non_copilot_models = ["gpt-4o", "claude-3-sonnet", "openai/gpt-4"]
        for model in non_copilot_models:
            if GitHubCopilotConfig.is_github_copilot_model(model):
                print(f"  ❌ Incorrectly detected {model} as GitHub Copilot model")
                return False
        
        print("  ✅ Model detection working correctly")
        return True
    except Exception as e:
        print(f"  ❌ Model detection failed: {e}")
        return False

def test_configuration():
    """Test GitHub Copilot configuration."""
    print("\n🔍 Testing configuration...")
    try:
        from openhands.core.config import LLMConfig
        from openhands.llm.github_copilot import GitHubCopilotConfig
        from pydantic import SecretStr
        
        # Test configuration with API key
        config = LLMConfig(
            model="github_copilot/gpt-4.1",
            api_key=SecretStr("test_token")
        )
        
        configured = GitHubCopilotConfig.configure_for_copilot(config)
        
        if configured.custom_llm_provider != "github_copilot":
            print(f"  ❌ Wrong provider: {configured.custom_llm_provider}")
            return False
        
        if configured.base_url != GitHubCopilotConfig.DEFAULT_API_BASE:
            print(f"  ❌ Wrong base URL: {configured.base_url}")
            return False
        
        if not configured.api_key:
            print("  ❌ API key not preserved")
            return False
        
        print("  ✅ Configuration working correctly")
        return True
    except Exception as e:
        print(f"  ❌ Configuration failed: {e}")
        return False

def test_environment_token():
    """Test GitHub token from environment variable."""
    print("\n🔍 Testing environment token...")
    try:
        from openhands.core.config import LLMConfig
        from openhands.llm.github_copilot import GitHubCopilotConfig
        import os
        
        # Set test token
        test_token = "ghp_test_token_12345"
        original_token = os.environ.get("GITHUB_TOKEN")
        os.environ["GITHUB_TOKEN"] = test_token
        
        try:
            config = LLMConfig(model="github_copilot/gpt-4o")
            configured = GitHubCopilotConfig.configure_for_copilot(config)
            
            if not configured.api_key:
                print("  ❌ Environment token not picked up")
                return False
            
            if configured.api_key.get_secret_value() != test_token:
                print(f"  ❌ Wrong token value: expected {test_token}, got {configured.api_key.get_secret_value()}")
                return False
            
            print("  ✅ Environment token working correctly")
            return True
        finally:
            # Restore original token
            if original_token:
                os.environ["GITHUB_TOKEN"] = original_token
            else:
                os.environ.pop("GITHUB_TOKEN", None)
                
    except Exception as e:
        print(f"  ❌ Environment token test failed: {e}")
        return False

def test_llm_initialization(model: str = "github_copilot/gpt-4.1"):
    """Test LLM initialization with GitHub Copilot."""
    print(f"\n🔍 Testing LLM initialization with {model}...")
    try:
        from openhands.core.config import LLMConfig
        from openhands.llm import LLM
        from pydantic import SecretStr
        
        # Test with API key
        config = LLMConfig(
            model=model,
            api_key=SecretStr("test_token")
        )
        
        llm = LLM(config)
        
        if llm.config.custom_llm_provider != "github_copilot":
            print(f"  ❌ Wrong provider: {llm.config.custom_llm_provider}")
            return False
        
        if llm.config.model != model:
            print(f"  ❌ Wrong model: {llm.config.model}")
            return False
        
        print(f"  ✅ LLM initialization successful for {model}")
        return True
    except Exception as e:
        print(f"  ❌ LLM initialization failed: {e}")
        return False

def test_multiple_models():
    """Test multiple GitHub Copilot models."""
    print("\n🔍 Testing multiple models...")
    
    models = [
        "github_copilot/gpt-4.1",
        "github_copilot/gpt-4o",
        "github_copilot/claude-sonnet-4"
    ]
    
    success_count = 0
    for model in models:
        try:
            if test_llm_initialization(model):
                success_count += 1
                print(f"  ✅ {model} - OK")
            else:
                print(f"  ❌ {model} - Failed")
        except Exception as e:
            print(f"  ❌ {model} - {e}")
    
    if success_count == len(models):
        print(f"  ✅ All {len(models)} models configured successfully")
        return True
    else:
        print(f"  ❌ Only {success_count}/{len(models)} models configured successfully")
        return False

def test_live_completion(model: str = "github_copilot/gpt-4.1"):
    """Test live completion with GitHub Copilot (requires authentication)."""
    print(f"\n🔍 Testing live completion with {model}...")
    
    # Check if live test is enabled
    if not os.getenv("GITHUB_COPILOT_LIVE_TEST"):
        print("  ✅ Skipped (set GITHUB_COPILOT_LIVE_TEST=1 to enable)")
        return True
    
    try:
        from openhands.core.config import LLMConfig
        from openhands.llm import LLM
        
        config = LLMConfig(model=model, temperature=0.1)
        llm = LLM(config)
        
        # Test simple completion
        messages = [
            {
                "role": "user",
                "content": "Write a simple Python function that returns 'Hello, World!'"
            }
        ]
        
        print("  🔄 Making API call...")
        response = llm.completion(messages=messages)
        
        if not response or not response.choices:
            print("  ❌ No response received")
            return False
        
        content = response.choices[0].message.content
        if not content or len(content) < 10:
            print("  ❌ Invalid response content")
            return False
        
        print(f"  ✅ Live completion successful! Response length: {len(content)} chars")
        print(f"  📝 Preview: {content[:100]}...")
        return True
        
    except Exception as e:
        print(f"  ❌ Live completion failed: {e}")
        return False

def test_oauth_status():
    """Test OAuth authentication status."""
    print("\n🔍 Testing OAuth authentication status...")
    try:
        from openhands.llm.github_copilot_auth import GitHubCopilotAuthManager
        
        auth_manager = GitHubCopilotAuthManager()
        is_auth = auth_manager.is_authenticated()
        
        if is_auth:
            print("  ✅ OAuth authenticated")
            try:
                api_key = auth_manager.get_api_key()
                if api_key:
                    print(f"  ✅ API key available (length: {len(api_key)})")
                else:
                    print("  ⚠️  OAuth authenticated but no API key")
            except Exception as e:
                print(f"  ⚠️  OAuth authenticated but API key error: {e}")
        else:
            print("  ℹ️  OAuth not authenticated (use 'openhands auth github-copilot')")
        
        return True
    except Exception as e:
        print(f"  ❌ OAuth status check failed: {e}")
        return False

def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate GitHub Copilot provider")
    parser.add_argument("--live-test", action="store_true", help="Enable live API testing")
    parser.add_argument("--model", default="github_copilot/gpt-4.1", help="Model to test")
    args = parser.parse_args()
    
    if args.live_test:
        os.environ["GITHUB_COPILOT_LIVE_TEST"] = "1"
    
    print("🚀 GitHub Copilot Provider Validation")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Model Detection", test_model_detection),
        ("Configuration", test_configuration),
        ("Environment Token", test_environment_token),
        ("OAuth Status", test_oauth_status),
        ("LLM Initialization", lambda: test_llm_initialization(args.model)),
        ("Multiple Models", test_multiple_models),
        ("Live Completion", lambda: test_live_completion(args.model)),
    ]
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                failed_tests.append(test_name)
        except Exception as e:
            print(f"  ❌ {test_name} - Exception: {e}")
            failed += 1
            failed_tests.append(f"{test_name}: {e}")
    
    print(f"\n📊 Test Summary: {passed}/{passed + failed} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"  • {test}")
    
    if failed == 0:
        print("\n🎉 All tests passed! GitHub Copilot provider is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
