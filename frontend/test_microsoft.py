#!/usr/bin/env python3
"""
Test script for Howdy Test Agent with Microsoft Homepage
Demonstrates real Stagehand agent execution on a live website
"""

import asyncio
import sys
import os
import json

# Add the frontend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_agent import HowdyTestAgent

async def test_microsoft_homepage():
    """Test the Microsoft homepage using Stagehand agent"""
    print("🚀 Testing Howdy Test Agent with Microsoft Homepage")
    print("=" * 60)
    print("This test will use Stagehand to interact with microsoft.com")
    print("=" * 60)
    
    # Create agent instance
    agent = HowdyTestAgent(web_port=3000, backend_port=443)
    print("\n✅ Agent instance created")
    
    try:
        # Initialize Stagehand
        print("\n1️⃣  Initializing Stagehand...")
        success = await agent.initialize_stagehand()
        
        if not success:
            print("❌ Failed to initialize Stagehand")
            print("   Make sure you have OPENAI_API_KEY in your .env file")
            return
        
        print("✅ Stagehand initialized successfully")
        
        # Navigate to Microsoft homepage
        print("\n2️⃣  Navigating to Microsoft homepage...")
        target_url = "https://www.microsoft.com"
        await agent.page.goto(target_url)
        print(f"   ✅ Navigated to {target_url}")
        
        # Define test scenarios for Microsoft homepage
        print("\n3️⃣  Defining test scenarios...")
        test_scenarios = [
            "Verify the Microsoft homepage loaded correctly and identify the main elements",
            "Find and describe the main navigation menu items",
            "Check if a search functionality is present and describe its location",
            "Observe any featured products or promotions on the homepage",
            "Identify the footer links and sections"
        ]
        
        print(f"   Created {len(test_scenarios)} test scenarios:")
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"   {i}. {scenario}")
        
        # Execute tests with Stagehand
        print("\n4️⃣  Executing tests with Stagehand agent...")
        print("   (This may take a few minutes...)")
        
        results = []
        for i, scenario in enumerate(test_scenarios):
            try:
                print(f"\n   Test {i+1}/{len(test_scenarios)}: {scenario}")
                
                # Create agent instance
                stagehand_agent = agent.stagehand.agent()
                
                # Execute the scenario
                agent_result = await stagehand_agent.execute({
                    'instruction': scenario,
                    'maxSteps': 20,
                    'autoScreenshot': True,
                    'waitBetweenActions': 1000  # 1 second between actions
                })
                
                # Store result
                agent.execution_results.append({
                    "scenario": scenario,
                    "result": agent_result,
                    "timestamp": __import__('datetime').datetime.now().isoformat(),
                    "index": i
                })
                
                # Extract screenshots if available
                if isinstance(agent_result, dict) and 'screenshots' in agent_result:
                    screenshots = agent_result.get('screenshots', [])
                    if screenshots:
                        screenshot = screenshots[-1] if isinstance(screenshots, list) else screenshots
                        agent.screenshots.append(screenshot)
                        print(f"   ✅ Test completed with screenshot")
                else:
                    print(f"   ✅ Test completed")
                
                results.append({
                    'scenario': scenario,
                    'success': True,
                    'result': agent_result
                })
                
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
                results.append({
                    'scenario': scenario,
                    'success': False,
                    'error': str(e)
                })
        
        # Display results summary
        print("\n" + "=" * 60)
        print("5️⃣  Test Results Summary")
        print("=" * 60)
        
        successful_tests = sum(1 for r in results if r['success'])
        failed_tests = len(results) - successful_tests
        
        print(f"\n📊 Total Tests: {len(results)}")
        print(f"✅ Passed: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        print("\n📝 Detailed Results:")
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"\n{i}. {status} {result['scenario']}")
            
            if result['success'] and isinstance(result.get('result'), dict):
                agent_result = result['result']
                
                # Display actions taken
                if 'actions' in agent_result:
                    actions = agent_result['actions']
                    print(f"   Actions taken: {len(actions) if isinstance(actions, list) else 'N/A'}")
                    if isinstance(actions, list) and actions:
                        for action in actions[:3]:  # Show first 3 actions
                            print(f"   - {action}")
                        if len(actions) > 3:
                            print(f"   ... and {len(actions) - 3} more")
                
                # Display success status
                if 'success' in agent_result:
                    print(f"   Success: {agent_result['success']}")
                
                # Display messages
                if 'messages' in agent_result:
                    messages = agent_result['messages']
                    if isinstance(messages, list) and messages:
                        print(f"   Messages: {messages[0]}")
            
            elif not result['success']:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Display collected data
        print("\n" + "=" * 60)
        print("6️⃣  Collected Data")
        print("=" * 60)
        print(f"\n📦 Execution Results: {len(agent.execution_results)}")
        print(f"📸 Screenshots: {len(agent.screenshots)}")
        print(f"👁️  Observations: {len(agent.observations)}")
        
        # Save results to file
        print("\n7️⃣  Saving results to file...")
        results_file = "microsoft_test_results.json"
        
        output = {
            "test_summary": {
                "total_tests": len(results),
                "passed": successful_tests,
                "failed": failed_tests,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            },
            "execution_results": agent.execution_results,
            "screenshots": agent.screenshots,
            "observations": agent.observations
        }
        
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"✅ Results saved to: {results_file}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ Microsoft Homepage Test Completed!")
        print("=" * 60)
        
        if successful_tests == len(results):
            print("\n🎉 All tests passed successfully!")
        elif successful_tests > 0:
            print(f"\n⚠️  {successful_tests}/{len(results)} tests passed")
        else:
            print("\n❌ All tests failed - check your configuration")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close Stagehand
        print("\n🔒 Closing Stagehand session...")
        await agent.close_stagehand()
        print("✅ Session closed")

async def test_microsoft_quick():
    """Quick test with Microsoft homepage - single scenario"""
    print("🚀 Quick Test: Microsoft Homepage")
    print("=" * 60)
    
    agent = HowdyTestAgent(web_port=3000, backend_port=443)
    
    try:
        # Initialize Stagehand
        print("Initializing Stagehand...")
        success = await agent.initialize_stagehand()
        
        if not success:
            print("❌ Failed to initialize Stagehand")
            return
        
        print("✅ Stagehand initialized")
        
        # Navigate to Microsoft homepage
        print("\nNavigating to https://www.microsoft.com...")
        await agent.page.goto("https://www.microsoft.com")
        print("✅ Page loaded")
        
        # Single test scenario
        scenario = "Describe what you see on this Microsoft homepage"
        
        print(f"\nExecuting: {scenario}")
        print("(This may take a minute...)\n")
        
        # Create and execute agent
        stagehand_agent = agent.stagehand.agent()
        
        agent_result = await stagehand_agent.execute({
            'instruction': scenario,
            'maxSteps': 10,
            'autoScreenshot': True,
            'waitBetweenActions': 500
        })
        
        # Display result
        print("=" * 60)
        print("Result:")
        print("=" * 60)
        
        if isinstance(agent_result, dict):
            print(json.dumps(agent_result, indent=2, default=str))
        else:
            print(agent_result)
        
        print("\n✅ Quick test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.close_stagehand()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Microsoft Homepage with Stagehand')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick test with single scenario')
    
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(test_microsoft_quick())
    else:
        asyncio.run(test_microsoft_homepage())

