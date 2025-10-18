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
    stagehand_api_url = os.getenv("STAGEHAND_API_URL", "http://localhost:443")
    model_name = os.getenv("STAGEHAND_MODEL", "tngtech/deepseek-r1t-chimera:free")
    
    # Target URL - using microsoft.com for testing
    target_url = "https://www.microsoft.com"
    
    print(f"🚀 Starting Stagehand Browser Automation")
    print(f"📋 Changelog: {changelog}")
    print(f"🌐 Target URL: {target_url}")
    print(f"🤖 Model: {model_name}")
    print(f"🔗 API URL: {stagehand_api_url}")
    print("-" * 80)
    
    # Initialize Stagehand configuration
    config = StagehandConfig(
        env="LOCAL",  # Run local browser, not Browserbase
        headless=False,  # Run in headed mode to see the browser
        model_name=model_name,
        verbose=2,  # Medium verbosity
    )
    
    # Create Stagehand client
    stagehand = Stagehand(
        config=config,
        server_url=stagehand_api_url,  # Point to our FastAPI backend
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

