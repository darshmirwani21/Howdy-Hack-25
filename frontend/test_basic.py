"""
Quick test script for the Howdy Test Agent
Run this to test the basic functionality WITHOUT a web app running
Tests the agent's internal methods and data flow
"""

import asyncio
import sys
import os
import json

# Add the frontend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_agent import HowdyTestAgent

async def test_basic_functionality():
    """Test basic functionality of the test agent without Stagehand"""
    print("🧪 Testing Howdy Test Agent (Basic Functionality)")
    print("=" * 60)
    print("NOTE: This tests internal methods WITHOUT Stagehand/web app")
    print("=" * 60)
    
    # Create agent instance
    agent = HowdyTestAgent(web_port=3000, backend_port=443)
    print("\n✅ Agent instance created")
    print(f"   Web port: {agent.web_port}")
    print(f"   Backend port: {agent.backend_port}")
    print(f"   Screenshots directory created: ./screenshots/")
    
    # Test 1: Prompt parsing
    print("\n1️⃣  Testing prompt parsing...")
    test_prompts = [
        "Test the login functionality",
        "Test form submission and validation",
        "Test navigation menu",
        "Generic test"
    ]
    
    for prompt in test_prompts:
        agent_response = await agent.agent_method(prompt)
        print(f"   Prompt: '{prompt}'")
        print(f"   → Generated {len(agent_response['test_scenarios'])} scenarios")
        print(f"   → Scenarios: {agent_response['test_scenarios'][:2]}...")
    
    # Test 2: Data storage
    print("\n2️⃣  Testing data storage...")
    print(f"   execution_results: {len(agent.execution_results)} items")
    print(f"   screenshots: {len(agent.screenshots)} items")
    print(f"   observations: {len(agent.observations)} items")
    
    # Test 3: Fallback simulation (no Stagehand)
    print("\n3️⃣  Testing fallback simulation mode...")
    test_scenarios = ["Navigate to homepage", "Click login button", "Fill form"]
    simulation_results = await agent._fallback_simulation(test_scenarios)
    print(f"   Simulated {len(simulation_results)} tests")
    for i, result in enumerate(simulation_results):
        status = "✅" if result.success else "❌"
        print(f"   {status} Test {i+1}: {result.message}")
    
    # Test 4: Backend API connection check
    print("\n4️⃣  Testing backend API connection...")
    backend_status = await agent.test_backend_api_connection()
    print(f"   Status: {backend_status['status']}")
    if backend_status['status'] == 'disconnected':
        print(f"   ⚠️  Backend not running (expected for basic test)")
    
    # Test 5: Web server connection check
    print("\n5️⃣  Testing web server connection...")
    server_status = await agent.create_live_server_connection()
    if server_status:
        print(f"   ✅ Web server connected on port {agent.web_port}")
    else:
        print(f"   ⚠️  Web server not running on port {agent.web_port} (expected)")
    
    # Test 6: Payload preparation
    print("\n6️⃣  Testing payload preparation...")
    # Simulate some data
    agent.execution_results.append({
        "scenario": "Test scenario",
        "result": {"success": True, "actions": ["action1"], "screenshots": ["screenshot1.png"]},
        "timestamp": "2025-01-01T12:00:00",
        "index": 0
    })
    agent.screenshots.append("screenshot1.png")
    agent.observations.append({
        "port": 3000,
        "status": "observed",
        "observation": "test",
        "timestamp": "2025-01-01T12:00:00"
    })
    
    payload = {
        "execution_results": agent.execution_results,
        "screenshot_references": agent.screenshots,
        "observations": agent.observations,
        "metadata": {
            "total_executions": len(agent.execution_results),
            "total_screenshots": len(agent.screenshots),
            "total_observations": len(agent.observations),
            "web_port": agent.web_port,
            "timestamp": "2025-01-01T12:00:00"
        }
    }
    
    print(f"   Payload structure:")
    print(f"   - execution_results: {len(payload['execution_results'])} items")
    print(f"   - screenshot_references: {len(payload['screenshot_references'])} items")
    print(f"   - observations: {len(payload['observations'])} items")
    print(f"   - metadata: {payload['metadata']}")
    
    # Test 7: JSON serialization
    print("\n7️⃣  Testing JSON serialization...")
    try:
        json_payload = json.dumps(payload, indent=2)
        print(f"   ✅ Payload serializes to JSON ({len(json_payload)} bytes)")
    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Basic functionality test completed!")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Start your web app on port 3000")
    print("2. Start your backend on port 443")
    print("3. Run: python test_agent.py --prompt 'Test login'")
    print("\nOR test with Stagehand:")
    print("python test_agent.py --prompt 'Navigate to https://example.com'")

async def test_with_stagehand():
    """
    Test with Stagehand initialization (requires API keys)
    Only run this if you have OPENAI_API_KEY set
    """
    print("\n🚀 Testing with Stagehand initialization...")
    print("=" * 60)
    
    agent = HowdyTestAgent(web_port=3000, backend_port=443)
    
    try:
        # Try to initialize Stagehand
        print("Attempting to initialize Stagehand...")
        success = await agent.initialize_stagehand()
        
        if success:
            print("✅ Stagehand initialized successfully!")
            print("   You can now test with real web apps")
            
            # Close Stagehand
            await agent.close_stagehand()
        else:
            print("❌ Stagehand initialization failed")
            print("   Check your .env file for OPENAI_API_KEY")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure you have:")
        print("   1. OPENAI_API_KEY in .env file")
        print("   2. Stagehand installed: pip install stagehand")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Howdy Test Agent')
    parser.add_argument('--with-stagehand', action='store_true', 
                       help='Test with Stagehand initialization (requires API keys)')
    
    args = parser.parse_args()
    
    if args.with_stagehand:
        asyncio.run(test_with_stagehand())
    else:
        asyncio.run(test_basic_functionality())
