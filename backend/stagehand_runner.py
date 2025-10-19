#!/usr/bin/env python3
"""
Stagehand CLI Runner for Browser Automation Testing

This script accepts an AI-generated changelog description and uses Stagehand
in agent mode to automatically test the application at http://localhost:3000.
"""

import sys
import os
import asyncio
from dotenv import load_dotenv
from stagehand import Stagehand, StagehandConfig

# Load environment variables
load_dotenv()


async def run_test(changelog: str):
    """
    Run automated browser tests using Stagehand agent mode.
    
    Args:
        changelog: Detailed AI-generated changelog describing what to test
    """
    # Get configuration from environment
    use_agent = os.getenv("USE_AGENT", "false").lower() == "true"
    
    if use_agent:
        stagehand_api_url = os.getenv("STAGEHAND_API_URL", "http://localhost:443")
        model_name = os.getenv("STAGEHAND_MODEL", "tngtech/deepseek-r1t-chimera:free")
        model_api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("MODEL_API_KEY")
        
        if not model_api_key:
            print("❌ Error: MODEL_API_KEY or OPENROUTER_API_KEY environment variable is required for agent mode")
            print("Please set your OpenRouter API key:")
            print("  export OPENROUTER_API_KEY='your-api-key-here'")
            print("\nOr run without agent mode (basic browser automation only):")
            print("  export USE_AGENT=false")
            sys.exit(1)
    
    # Target URL - using microsoft.com for testing
    target_url = "https://www.microsoft.com"
    
    print(f"🚀 Starting Stagehand Browser Automation")
    print(f"📋 Changelog: {changelog}")
    print(f"🌐 Target URL: {target_url}")
    print(f"🤖 Agent Mode: {'Enabled' if use_agent else 'Disabled (Basic automation only)'}")
    if use_agent:
        print(f"🤖 Model: {model_name}")
        print(f"🔗 API URL: {stagehand_api_url}")
    print("-" * 80)
    
    # Initialize Stagehand configuration
    if use_agent:
        config = StagehandConfig(
            env="LOCAL",  # Run local browser, not Browserbase
            headless=False,  # Run in headed mode to see the browser
            verbose=2,  # Medium verbosity
            model_name=model_name,
            model_api_key=model_api_key,  # API key for the LLM (OpenRouter)
            model_client_options={
                "base_url": stagehand_api_url,
            }
        )
    else:
        # Minimal config without AI - just basic browser automation
        config = StagehandConfig(
            env="LOCAL",  # Run local browser, not Browserbase
            headless=False,  # Run in headed mode to see the browser
            verbose=2,  # Medium verbosity
        )
    
    # Create Stagehand client
    stagehand = Stagehand(
        config=config,
    )
    
    try:
        # Initialize Stagehand
        print("🔧 Initializing Stagehand...")
        await stagehand.init()
        print("✅ Stagehand initialized successfully")
        
        # Navigate to target URL
        print(f"🌐 Navigating to {target_url}...")
        page = stagehand.page
        await page.goto(target_url)
        print("✅ Page loaded successfully")
        
        if use_agent:
            # Create agent for autonomous testing
            print("🤖 Creating Stagehand agent...")
            agent = stagehand.agent()
            print("✅ Agent created")
            
            # Execute test based on changelog
            print("\n🧪 Starting automated testing...")
            print(f"📝 Test description: {changelog}")
            print("-" * 80)
            
            result = await agent.execute(changelog)
            
            print("-" * 80)
            print("✅ Testing completed successfully!")
            print(f"📊 Result: {result}")
        else:
            # Basic automation test without AI
            print("\n🧪 Performing basic browser automation test...")
            print(f"📝 Description: {changelog}")
            print("-" * 80)
            
            # Get page title
            title = await page.title()
            print(f"📄 Page Title: {title}")
            
            # Get page URL
            url = page.url
            print(f"🔗 Current URL: {url}")
            
            # Wait a bit to see the page
            print("⏳ Waiting 3 seconds for you to see the page...")
            await asyncio.sleep(3)
            
            print("-" * 80)
            print("✅ Basic automation test completed successfully!")
            print("🎉 Stagehand is working! You can now enable agent mode with USE_AGENT=true")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        await stagehand.close()
        print("✅ Cleanup complete")


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: python stagehand_runner.py '<detailed changelog description>'")
        print("\nExample:")
        print("  python stagehand_runner.py 'Test the login functionality after recent changes to the authentication module. Verify that users can successfully log in with valid credentials and see appropriate error messages for invalid credentials.'")
        sys.exit(1)
    
    # Get the changelog from command line argument
    changelog = sys.argv[1]
    
    # Run the async test function
    asyncio.run(run_test(changelog))


if __name__ == "__main__":
    main()

