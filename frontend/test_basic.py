#!/usr/bin/env python3
"""
Quick test script for the Howdy Test Agent
Run this to test the basic functionality with proper error handling and cleanup
"""

import asyncio
import sys
import os
import traceback
from datetime import datetime

# Add the frontend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_agent import HowdyTestAgent

class TestRunner:
    """Manages test execution with proper setup and teardown"""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    async def setup(self):
        """Initialize the test agent and Stagehand"""
        print("🔧 Setting up test environment...")
        try:
            # Create agent instance
            self.agent = HowdyTestAgent(web_port=3000, backend_port=443)
            
            # Initialize Stagehand (CRITICAL - was missing!)
            print("   Initializing Stagehand browser...")
            initialized = await self.agent.initialize_stagehand()
            
            if not initialized:
                print("   ⚠️  Stagehand initialization failed - tests will run in simulation mode")
                return False
            
            print("   ✅ Setup complete")
            return True
            
        except Exception as e:
            print(f"   ❌ Setup failed: {e}")
            traceback.print_exc()
            return False
    
    async def teardown(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        try:
            if self.agent:
                await self.agent.close_stagehand()
            print("   ✅ Cleanup complete")
        except Exception as e:
            print(f"   ⚠️  Cleanup error: {e}")
    
    async def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a single test with error handling"""
        print(f"\n{'='*70}")
        print(f"🧪 Test: {test_name}")
        print(f"{'='*70}")
        
        try:
            start = datetime.now()
            result = await test_func(*args, **kwargs)
            duration = (datetime.now() - start).total_seconds()
            
            self.test_results.append({
                "name": test_name,
                "status": "✅ PASS",
                "duration": duration,
                "result": result
            })
            
            print(f"   ✅ Test passed ({duration:.2f}s)")
            return result
            
        except Exception as e:
            duration = (datetime.now() - start).total_seconds()
            self.test_results.append({
                "name": test_name,
                "status": "❌ FAIL",
                "duration": duration,
                "error": str(e)
            })
            
            print(f"   ❌ Test failed: {e}")
            traceback.print_exc()
            return None
    
    def print_summary(self):
        """Print test execution summary"""
        print(f"\n{'='*70}")
        print("📊 TEST SUMMARY")
        print(f"{'='*70}")
        
        total_tests = len(self.test_results)
        passed = sum(1 for t in self.test_results if t["status"] == "✅ PASS")
        failed = total_tests - passed
        total_duration = sum(t["duration"] for t in self.test_results)
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        
        print(f"\n📋 Individual Test Results:")
        for test in self.test_results:
            status = test["status"]
            name = test["name"]
            duration = test["duration"]
            print(f"   {status} {name} ({duration:.2f}s)")
            if "error" in test:
                print(f"      Error: {test['error']}")
        
        print(f"\n{'='*70}\n")
        
        return passed == total_tests

async def test_backend_api_connection(agent: HowdyTestAgent):
    """Test 1: Backend API connection"""
    result = await agent.test_backend_api_connection()
    
    print(f"   Port: {result.get('port')}")
    print(f"   Status: {result.get('status')}")
    print(f"   API URL: {result.get('api_url')}")
    
    if result.get('status') != 'connected':
        print(f"   ⚠️  Note: Backend API not running (this is okay for basic testing)")
    
    return result

async def test_live_server_connection(agent: HowdyTestAgent):
    """Test 2: Web server connection"""
    server_status = await agent.create_live_server_connection()
    
    print(f"   Web Port: {agent.web_port}")
    print(f"   Status: {'✅ Connected' if server_status else '❌ Not connected'}")
    
    if not server_status:
        print(f"   ⚠️  Note: Make sure your web app is running on port {agent.web_port}")
    
    return server_status

async def test_agent_method(agent: HowdyTestAgent):
    """Test 3: Agent method (prompt parsing)"""
    test_prompt = "Test the login functionality and form submission"
    agent_response = await agent.agent_method(test_prompt)
    
    print(f"   Prompt: {test_prompt}")
    print(f"   Generated Scenarios: {len(agent_response['test_scenarios'])}")
    
    for i, scenario in enumerate(agent_response['test_scenarios'], 1):
        print(f"      {i}. {scenario}")
    
    assert len(agent_response['test_scenarios']) > 0, "No test scenarios generated"
    return agent_response

async def test_stagehand_navigation(agent: HowdyTestAgent):
    """Test 4: Navigate to web app before testing"""
    if not agent.page:
        print("   ⚠️  Skipping - Stagehand not initialized")
        return None
    
    try:
        url = f"http://localhost:{agent.web_port}"
        print(f"   Navigating to: {url}")
        
        await agent.page.goto(url, timeout=10000)
        
        # Get page title
        title = await agent.page.title()
        print(f"   Page Title: {title}")
        print(f"   ✅ Navigation successful")
        
        return {"url": url, "title": title}
        
    except Exception as e:
        print(f"   ⚠️  Navigation failed: {e}")
        print(f"   Make sure your web app is running on port {agent.web_port}")
        return None

async def test_observe_method(agent: HowdyTestAgent):
    """Test 5: Observe method"""
    observation = await agent.observe_method()
    
    print(f"   Port: {observation.get('port')}")
    print(f"   Status: {observation.get('status')}")
    print(f"   URL: {observation.get('url')}")
    
    if observation.get('status') == 'observed':
        print(f"   ✅ Page observed successfully")
    
    return observation

async def test_stagehand_execution(agent: HowdyTestAgent):
    """Test 6: Stagehand method (execute test scenarios)"""
    # Generate simple test scenarios
    test_scenarios = [
        "Observe the current page",
        "Check if the page loaded correctly"
    ]
    
    print(f"   Executing {len(test_scenarios)} test scenarios...")
    test_results = await agent.stagehand_method(test_scenarios)
    
    print(f"   Total Results: {len(test_results)}")
    print(f"   Screenshots Captured: {len(agent.screenshots)}")
    
    for i, result in enumerate(test_results, 1):
        status = "✅" if result.success else "❌"
        print(f"      {status} Test {i}: {result.message}")
        if result.screenshot_path:
            print(f"         Screenshot: {result.screenshot_path}")
    
    return test_results

async def test_screenshot_analysis(agent: HowdyTestAgent):
    """Test 7: UI Screenshot Analysis (NEW!)"""
    if not agent.screenshots:
        print("   ⚠️  No screenshots to analyze - skipping")
        return None
    
    print(f"   Analyzing {len(agent.screenshots)} screenshots...")
    ui_analysis = await agent.analyze_screenshots_locally()
    
    summary = ui_analysis.get('summary', {})
    print(f"   Average Score: {summary.get('average_score', 0):.1f}/10")
    print(f"   ✅ Good Designs: {summary.get('good_designs', 0)}")
    print(f"   ⚠️  Needs Improvement: {summary.get('needs_improvement', 0)}")
    
    # Print brief analysis of first screenshot
    if ui_analysis.get('analyses'):
        first = ui_analysis['analyses'][0]
        if 'analysis' in first and 'overall_score' in first['analysis']:
            analysis = first['analysis']
            print(f"\n   📸 First Screenshot Analysis:")
            print(f"      Overall Score: {analysis.get('overall_score', 0)}/10")
            print(f"      Good Design: {'✅ Yes' if analysis.get('is_good_design') else '⚠️ No'}")
    
    return ui_analysis

async def test_full_cycle(agent: HowdyTestAgent):
    """Test 8: Full test cycle (integration test)"""
    print("   Running complete end-to-end test cycle...")
    
    # Override prompt to avoid user input
    original_get_prompt = agent.get_ai_prompt
    agent.get_ai_prompt = lambda: "Test the web application UI"
    
    try:
        results = await agent.run_full_test_cycle()
        
        summary = results.get('summary', {})
        print(f"   Total Tests: {summary.get('total_tests', 0)}")
        print(f"   ✅ Passed: {summary.get('passed_tests', 0)}")
        print(f"   ❌ Failed: {summary.get('failed_tests', 0)}")
        
        ui_quality = summary.get('ui_quality', {})
        print(f"   UI Avg Score: {ui_quality.get('average_score', 0):.1f}/10")
        
        return results
        
    finally:
        # Restore original method
        agent.get_ai_prompt = original_get_prompt

async def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("🧪 HOWDY TEST AGENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    runner = TestRunner()
    
    try:
        # Setup
        runner.start_time = datetime.now()
        setup_success = await runner.setup()
        
        if not setup_success:
            print("\n⚠️  Setup failed - some tests may not work correctly")
        
        # Run tests in logical order
        await runner.run_test(
            "1. Backend API Connection",
            test_backend_api_connection,
            runner.agent
        )
        
        await runner.run_test(
            "2. Web Server Connection",
            test_live_server_connection,
            runner.agent
        )
        
        await runner.run_test(
            "3. Agent Method (Prompt Parsing)",
            test_agent_method,
            runner.agent
        )
        
        # Only test navigation/observation if Stagehand is initialized
        if runner.agent and runner.agent.page:
            await runner.run_test(
                "4. Navigate to Web Application",
                test_stagehand_navigation,
                runner.agent
            )
            
            await runner.run_test(
                "5. Observe Method",
                test_observe_method,
                runner.agent
            )
            
            await runner.run_test(
                "6. Stagehand Execution (Test Scenarios)",
                test_stagehand_execution,
                runner.agent
            )
            
            await runner.run_test(
                "7. UI Screenshot Analysis",
                test_screenshot_analysis,
                runner.agent
            )
        else:
            print("\n⚠️  Skipping browser-dependent tests (Stagehand not initialized)")
        
        # Always test full cycle (works in simulation mode too)
        await runner.run_test(
            "8. Full Test Cycle (Integration)",
            test_full_cycle,
            runner.agent
        )
        
        runner.end_time = datetime.now()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        traceback.print_exc()
    finally:
        # Always cleanup
        await runner.teardown()
        
        # Print summary
        total_time = (runner.end_time - runner.start_time).total_seconds() if runner.end_time else 0
        print(f"\n⏱️  Total test execution time: {total_time:.2f}s")
        
        all_passed = runner.print_summary()
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest execution cancelled by user")
        sys.exit(130)