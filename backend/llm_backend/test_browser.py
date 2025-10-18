#!/usr/bin/env python3
"""
Simple Playwright test to verify browser automation works in Docker
"""

import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    print("🧪 Testing Playwright Browser in Docker")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("✅ Playwright started")
        
        # Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        print("✅ Browser launched")
        
        # Create a new page
        page = await browser.new_page()
        print("✅ Page created")
        
        # Navigate to Microsoft.com
        print("🌐 Navigating to https://www.microsoft.com...")
        await page.goto("https://www.microsoft.com", wait_until="networkidle")
        print(f"✅ Page loaded: {await page.title()}")
        
        # Take a screenshot
        await page.screenshot(path="/tmp/microsoft_screenshot.png")
        print("📸 Screenshot saved to /tmp/microsoft_screenshot.png")
        
        # Wait a bit to see the browser
        await asyncio.sleep(3)
        
        # Close browser
        await browser.close()
        print("✅ Browser closed")
        print("=" * 60)
        print("🎉 Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_browser())

