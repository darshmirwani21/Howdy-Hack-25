#!/usr/bin/env python3
"""
Quick test script for the Howdy Test Agent
Run this to test the basic functionality
"""

import asyncio
import sys
import os

# Add the frontend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_agent import HowdyTestAgent

async def test_basic_functionality():
    """Test basic functionality of the test agent"""
    print("🧪 Testing Howdy Test Agent...")
    
    # Create agent instance
    agent = HowdyTestAgent(web_port=3000, backend_port=443)
    
    # Test individual methods
    print("\n1. Testing observe method...")
    observation = await agent.observe_method()
    print(f"   Observation result: {observation}")
    
    print("\n2. Testing agent method...")
    test_prompt = "Test the login functionality and form submission"
    agent_response = await agent.agent_method(test_prompt)
    print(f"   Agent response: {len(agent_response['test_scenarios'])} test scenarios generated")
    
    print("\n3. Testing stagehand method...")
    test_results = await agent.stagehand_method(agent_response['test_scenarios'])
    print(f"   Stagehand results: {len(test_results)} tests executed")
    
    print("\n4. Testing live server connection...")
    server_status = await agent.create_live_server_connection()
    print(f"   Server connection: {'✅ Connected' if server_status else '❌ Not connected'}")
    
    print("\n✅ Basic functionality test completed!")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
