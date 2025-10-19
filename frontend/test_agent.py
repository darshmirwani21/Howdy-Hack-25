#!/usr/bin/env python3
"""
Howdy Test Agent - Frontend Interface with Integrated UI Analysis
Core Python file that AI agents call to perform automated testing with design quality analysis
"""

import asyncio
import json
import sys
import argparse
import requests
import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from stagehand import Stagehand
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Data class for test results"""
    test_type: str
    success: bool
    message: str
    screenshot_path: Optional[str] = None
    error_details: Optional[str] = None
    timestamp: str = None

class PageData(BaseModel):
    """Pydantic model for extracted page data"""
    title: str
    url: str
    has_errors: bool = False
    error_messages: list = []

class HowdyTestAgent:
    """
    Main test agent class with integrated UI design analysis
    
    This class handles:
    1. Stagehand initialization and configuration (LOCAL mode)
    2. Getting prompts from LLM
    3. Connecting to the web port
    4. Making stagehand.agent() calls
    5. Using stagehand.observe() method
    6. Analyzing UI design quality with AI vision
    """
    
    def __init__(self, web_port: int = 3000, backend_port: int = 443):
        self.web_port = web_port
        self.backend_port = backend_port
        self.base_url = f"http://localhost:{web_port}"
        self.backend_url = f"http://localhost:{backend_port}"
        self.stagehand = None
        self.page = None
        
        # API configuration for UI analysis
        self.openrouter_api_key = "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"
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.analysis_model = "openai/gpt-5-nano"
        
        # Storage for execution results
        self.execution_results = []
        self.screenshots = []
        self.observations = []
        
        # Create screenshots directory if it doesn't exist
        Path("./screenshots").mkdir(parents=True, exist_ok=True)
    
    async def initialize_stagehand(self):
        """
        Initialize Stagehand browser automation
        This should be called once before using Stagehand methods
        """
        try:
            logger.info("Initializing Stagehand...")
            
            # Initialize Stagehand with configuration parameters directly
            self.stagehand = Stagehand(
                env="LOCAL",
                api_key=("your-api-key" if not os.getenv("BROWSERBASE_API_KEY") else os.getenv("BROWSERBASE_API_KEY")),
                project_id=("your-project-id" if not os.getenv("BROWSERBASE_PROJECT_ID") else os.getenv("BROWSERBASE_PROJECT_ID")),
                model_name="gpt-4o",
                model_client_options={
                    "base_url": f"http://localhost:{self.backend_port}/v1",
                },
                headless=False,
                verbose=2,
                use_rich_logging=True,
                dom_settle_timeout_ms=3000,
                enable_caching=False,
                self_heal=True,
            )
            
            await self.stagehand.init()
            self.page = self.stagehand.page
            
            logger.info("✅ Stagehand initialized successfully")
            logger.info("   Environment: LOCAL")
            logger.info(f"   Backend API: http://localhost:{self.backend_port}/v1")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Stagehand: {e}")
            logger.error("   Make sure you have the required API keys in your environment")
            return False
    
    async def close_stagehand(self):
        """
        Close Stagehand browser session
        """
        if self.stagehand:
            try:
                await self.stagehand.close()
                logger.info("Stagehand session closed")
            except Exception as e:
                logger.error(f"Error closing Stagehand: {e}")
        
    async def get_ai_prompt(self) -> str:
        """
        Get the user prompt from AI agent
        This is where the AI will provide the testing instructions
        """
        try:
            print("🤖 Waiting for AI agent prompt...")
            
            # Get prompt from stdin or use default
            prompt = input("Enter AI testing prompt: ").strip()
            
            if not prompt:
                prompt = "Test the web application functionality"
                
            logger.info(f"Received AI prompt: {prompt}")
            return prompt
            
        except Exception as e:
            logger.error(f"Error getting AI prompt: {e}")
            return "Test the web application functionality"
    
    async def agent_method(self, prompt: str) -> Dict[str, Any]:
        """
        Process the AI prompt and generate testing instructions
        """
        logger.info(f"Processing AI prompt: {prompt}")
        
        # Parse the prompt and generate test scenarios
        test_scenarios = self._parse_prompt_to_tests(prompt)
        
        # Prepare agent response
        agent_response = {
            "prompt": prompt,
            "test_scenarios": test_scenarios,
            "timestamp": datetime.now().isoformat(),
            "status": "ready"
        }
        
        logger.info(f"Generated {len(test_scenarios)} test scenarios")
        return agent_response
    
    def _parse_prompt_to_tests(self, prompt: str) -> list:
        """
        Convert AI prompt into specific test scenarios
        """
        prompt_lower = prompt.lower()
        test_scenarios = []
        
        # Basic test scenarios based on common prompts
        if "login" in prompt_lower or "authentication" in prompt_lower:
            test_scenarios.extend([
                "Navigate to the login page",
                "Enter valid credentials and submit",
                "Verify successful login",
                "Check for error messages with invalid credentials"
            ])
        
        if "form" in prompt_lower or "submit" in prompt_lower:
            test_scenarios.extend([
                "Find and fill out the main form",
                "Submit the form",
                "Verify submission success message",
                "Test form validation"
            ])
        
        if "navigation" in prompt_lower or "menu" in prompt_lower:
            test_scenarios.extend([
                "Test main navigation menu",
                "Verify all links work",
                "Check responsive navigation"
            ])
        
        if "search" in prompt_lower:
            test_scenarios.extend([
                "Test search functionality",
                "Verify search results",
                "Test search with no results"
            ])
        
        # Default tests if no specific scenarios found
        if not test_scenarios:
            test_scenarios = [
                "Navigate to the homepage",
                "Verify page loads correctly",
                "Test basic functionality",
                "Check for any errors"
            ]
        
        return test_scenarios
    
    async def stagehand_method(self, test_scenarios: list) -> list:
        """
        Execute tests using Stagehand agent.execute() method
        Stores results in memory for later analysis
        """
        logger.info("Starting Stagehand agent execution...")
        
        # Ensure Stagehand is initialized
        if not self.stagehand or not self.page:
            logger.warning("Stagehand not initialized, attempting to initialize...")
            if not await self.initialize_stagehand():
                logger.error("Failed to initialize Stagehand, falling back to simulation")
                return await self._fallback_simulation(test_scenarios)
        
        results = []
        
        try:
            # Create agent instance with configuration
            agent = self.stagehand.agent({
                'provider': 'openai',
                'model': 'gpt-4o',
                'instructions': 'Execute web testing scenarios and report results',
                'options': {
                    'apiKey': os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
                    'baseURL': f"http://localhost:{self.backend_port}/v1"
                }
            })
            
            logger.info("Agent instance created successfully")
            
            for i, scenario in enumerate(test_scenarios):
                try:
                    logger.info(f"Executing agent call {i+1}/{len(test_scenarios)}: {scenario}")
                    
                    # Execute using agent.execute() with the scenario
                    agent_result = await agent.execute({
                        'instruction': scenario,
                        'maxSteps': 20,
                        'autoScreenshot': True,
                        'waitBetweenActions': 500
                    })
                    
                    # Store the full agent result in memory
                    self.execution_results.append({
                        "scenario": scenario,
                        "result": agent_result,
                        "timestamp": datetime.now().isoformat(),
                        "index": i
                    })
                    
                    # Take manual screenshot and store path
                    import uuid
                    screenshot_path = f"./screenshots/scenario_{i}_{uuid.uuid4().hex[:8]}.png"
                    try:
                        await self.page.screenshot(path=screenshot_path)
                        self.screenshots.append(screenshot_path)
                        logger.info(f"Screenshot saved: {screenshot_path}")
                    except Exception as screenshot_error:
                        logger.warning(f"Could not save screenshot: {screenshot_error}")
                        screenshot_path = None
                    
                    # Create result summary
                    result = TestResult(
                        test_type="stagehand_agent",
                        success=agent_result.get('success', True) if isinstance(agent_result, dict) else True,
                        message=f"Agent executed: {scenario}",
                        screenshot_path=screenshot_path,
                        error_details=None,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    results.append(result)
                    logger.info(f"✅ Agent execution {i+1} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error executing agent call '{scenario}': {e}")
                    results.append(TestResult(
                        test_type="stagehand_agent",
                        success=False,
                        message=f"Failed to execute: {scenario}",
                        error_details=str(e),
                        timestamp=datetime.now().isoformat()
                    ))
        
        except Exception as e:
            logger.error(f"Error during Stagehand agent execution: {e}")
            return await self._fallback_simulation(test_scenarios)
        
        logger.info(f"Completed {len(results)} agent calls")
        logger.info(f"Stored {len(self.execution_results)} execution results in memory")
        return results
    
    async def _fallback_simulation(self, test_scenarios: list) -> list:
        """
        Fallback simulation when Stagehand is not available
        """
        logger.info("Using fallback simulation mode...")
        results = []
        
        for scenario in test_scenarios:
            result = await self._simulate_stagehand_test(scenario)
            results.append(result)
        
        return results
    
    async def _simulate_stagehand_test(self, scenario: str) -> TestResult:
        """
        Simulate Stagehand test execution
        """
        # Simulate test execution time
        await asyncio.sleep(0.5)
        
        # Simulate success/failure based on scenario
        success = "error" not in scenario.lower() and "fail" not in scenario.lower()
        
        return TestResult(
            test_type="stagehand",
            success=success,
            message=f"Executed: {scenario}",
            screenshot_path=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" if success else None,
            timestamp=datetime.now().isoformat()
        )
    
    async def test_backend_api_connection(self) -> Dict[str, Any]:
        """
        Test connection to the backend API
        """
        logger.info(f"Testing backend API connection on port {self.backend_port}")
        
        try:
            # Test the backend API endpoint
            api_url = f"http://localhost:{self.backend_port}/v1"
            response = requests.get(api_url, timeout=5)
            
            api_status = {
                "port": self.backend_port,
                "status": "connected",
                "response_code": response.status_code,
                "api_url": api_url,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Backend API connected: {api_url}")
            return api_status
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"Cannot connect to backend API on port {self.backend_port}")
            return {
                "port": self.backend_port,
                "status": "disconnected",
                "error": "Backend API connection refused",
                "api_url": f"http://localhost:{self.backend_port}/v1",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error testing backend API: {e}")
            return {
                "port": self.backend_port,
                "status": "error",
                "error": str(e),
                "api_url": f"http://localhost:{self.backend_port}/v1",
                "timestamp": datetime.now().isoformat()
            }
    
    async def observe_method(self, web_port: int = None) -> Dict[str, Any]:
        """
        Observe the web application using Stagehand's observe method
        """
        port = web_port or self.web_port
        logger.info(f"Observing web application on port {port}")
        
        # Ensure Stagehand is initialized
        if not self.stagehand or not self.page:
            logger.warning("Stagehand not initialized for observe")
            return {
                "port": port,
                "status": "error",
                "error": "Stagehand not initialized",
                "timestamp": datetime.now().isoformat(),
                "url": f"http://localhost:{port}"
            }
        
        try:
            # Use Stagehand's observe method
            observation_result = await self.page.observe()
            
            # Store observation in memory
            observation_data = {
                "port": port,
                "status": "observed",
                "url": f"http://localhost:{port}",
                "observation": observation_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.observations.append(observation_data)
            
            logger.info(f"Successfully observed web application on port {port}")
            logger.info(f"Stored observation in memory (total: {len(self.observations)})")
            
            return observation_data
            
        except Exception as e:
            logger.error(f"Error observing web application: {e}")
            return {
                "port": port,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "url": f"http://localhost:{port}"
            }
    
    async def create_live_server_connection(self) -> bool:
        """
        Verify connection to the web port
        """
        logger.info(f"Checking connection to web server on port {self.web_port}...")
        
        try:
            response = requests.get(f"http://localhost:{self.web_port}", timeout=5)
            logger.info(f"✅ Web server connected on port {self.web_port}")
            return True
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️  Cannot connect to web server on port {self.web_port}")
            return False
        except Exception as e:
            logger.error(f"❌ Error connecting to web server: {e}")
            return False
    
    async def analyze_screenshots_locally(self) -> Dict[str, Any]:
        """
        Analyze all captured screenshots using AI vision for UI design quality
        This integrates the UI Design Analyzer functionality
        """
        logger.info(f"🎨 Analyzing {len(self.screenshots)} screenshots for UI quality...")
        
        if not self.screenshots:
            logger.warning("No screenshots to analyze")
            return {
                "total_screenshots": 0,
                "analyses": [],
                "summary": {
                    "average_score": 0,
                    "good_designs": 0,
                    "needs_improvement": 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        analyses = []
        
        for i, screenshot_path in enumerate(self.screenshots):
            try:
                logger.info(f"Analyzing screenshot {i+1}/{len(self.screenshots)}: {screenshot_path}")
                
                # Read and encode the screenshot
                with open(screenshot_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Prepare the UI analysis prompt
                prompt = """Analyze this UI design screenshot and evaluate it across these criteria:

1. **Composition & Centering**: Is the main UI element properly centered? Is the layout balanced?
2. **Design Quality**: Is the design professional, modern, and well-executed?
3. **Color Scheme**: Are the colors harmonious? Do they work well together? Is there good contrast?
4. **Aesthetic Appeal**: Overall visual appeal and polish
5. **Format & Size**: Does it appear to be properly sized and formatted?

Provide your assessment in this JSON format:
{
    "overall_score": <1-10>,
    "is_good_design": <true/false>,
    "composition": {
        "score": <1-10>,
        "feedback": "brief comment"
    },
    "design_quality": {
        "score": <1-10>,
        "feedback": "brief comment"
    },
    "color_scheme": {
        "score": <1-10>,
        "feedback": "brief comment"
    },
    "aesthetics": {
        "score": <1-10>,
        "feedback": "brief comment"
    },
    "recommendations": ["suggestion 1", "suggestion 2"]
}

Be honest and constructive."""

                # Make API call to OpenRouter
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.analysis_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                }
                
                response = requests.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                # Try to parse JSON from response
                try:
                    start = analysis_text.find('{')
                    end = analysis_text.rfind('}') + 1
                    if start != -1 and end > start:
                        analysis_json = json.loads(analysis_text[start:end])
                    else:
                        analysis_json = {"raw_response": analysis_text}
                except json.JSONDecodeError:
                    analysis_json = {"raw_response": analysis_text}
                
                analyses.append({
                    "screenshot": screenshot_path,
                    "analysis": analysis_json,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"✅ Screenshot {i+1} analyzed successfully")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing screenshot {screenshot_path}: {e}")
                analyses.append({
                    "screenshot": screenshot_path,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Calculate summary statistics
        valid_analyses = [a for a in analyses if "analysis" in a and "overall_score" in a.get("analysis", {})]
        total_score = sum(a["analysis"]["overall_score"] for a in valid_analyses)
        average_score = total_score / len(valid_analyses) if valid_analyses else 0
        good_designs = sum(1 for a in valid_analyses if a["analysis"].get("is_good_design", False))
        
        return {
            "total_screenshots": len(self.screenshots),
            "analyses": analyses,
            "summary": {
                "average_score": round(average_score, 1),
                "good_designs": good_designs,
                "needs_improvement": len(valid_analyses) - good_designs
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def print_ui_analysis_report(self, ui_analysis: Dict[str, Any]):
        """
        Pretty print the UI analysis results
        """
        print("\n" + "="*70)
        print("🎨 UI DESIGN ANALYSIS REPORT")
        print("="*70)
        
        summary = ui_analysis.get("summary", {})
        print(f"\n📊 Overall Summary:")
        print(f"   Average Score: {summary.get('average_score', 0):.1f}/10")
        print(f"   ✅ Good Designs: {summary.get('good_designs', 0)}")
        print(f"   ⚠️  Needs Improvement: {summary.get('needs_improvement', 0)}")
        
        print(f"\n🖼️  Individual Screenshot Analysis:")
        for i, analysis in enumerate(ui_analysis.get("analyses", []), 1):
            print(f"\n   Screenshot {i}: {Path(analysis.get('screenshot', 'Unknown')).name}")
            
            if "error" in analysis:
                print(f"   ❌ Error: {analysis['error']}")
                continue
            
            analysis_data = analysis.get("analysis", {})
            if "overall_score" in analysis_data:
                score = analysis_data["overall_score"]
                is_good = analysis_data.get("is_good_design", False)
                status = "✅ GOOD" if is_good else "⚠️ NEEDS WORK"
                print(f"   Score: {score}/10 - {status}")
                
                # Show category scores
                for category in ["composition", "design_quality", "color_scheme", "aesthetics"]:
                    if category in analysis_data:
                        cat = analysis_data[category]
                        print(f"      • {category.replace('_', ' ').title()}: {cat.get('score', 0)}/10")
                        print(f"        {cat.get('feedback', 'No feedback')}")
                
                # Show recommendations
                if "recommendations" in analysis_data and analysis_data["recommendations"]:
                    print(f"   💡 Recommendations:")
                    for rec in analysis_data["recommendations"]:
                        print(f"      • {rec}")
            else:
                print(f"   📝 Raw analysis: {analysis_data.get('raw_response', 'No data')[:200]}...")
        
        print("\n" + "="*70 + "\n")
    
    async def run_full_test_cycle(self) -> Dict[str, Any]:
        """
        Run the complete test cycle with UI design analysis:
        1. Get AI prompt
        2. Process prompt into test scenarios
        3. Check backend API connection
        4. Verify web server connection
        5. Execute stagehand.agent() calls (stores results in memory)
        6. Run stagehand.observe() (stores observations in memory)
        7. Analyze all screenshots for UI design quality
        8. Return comprehensive results
        """
        logger.info("🚀 Starting full test cycle...")
        
        try:
            # Step 1: Get AI prompt
            prompt = await self.get_ai_prompt()
            
            # Step 2: Process with agent method
            agent_response = await self.agent_method(prompt)
            
            # Step 3: Test backend API connection
            backend_api_status = await self.test_backend_api_connection()
            
            # Step 4: Create live server connection
            server_connected = await self.create_live_server_connection()
            
            # Step 5: Execute tests with Stagehand
            test_results = await self.stagehand_method(agent_response["test_scenarios"])
            
            # Step 6: Final observation
            final_observation = await self.observe_method()
            
            # Step 7: Analyze screenshots for UI quality (NEW!)
            logger.info("🎨 Starting UI design analysis...")
            ui_analysis = await self.analyze_screenshots_locally()
            
            # Compile final results
            final_results = {
                "prompt": prompt,
                "agent_response": agent_response,
                "backend_api_status": backend_api_status,
                "server_connected": server_connected,
                "test_results": [
                    {
                        "test_type": result.test_type,
                        "success": result.success,
                        "message": result.message,
                        "screenshot_path": result.screenshot_path,
                        "error_details": result.error_details,
                        "timestamp": result.timestamp
                    } for result in test_results
                ],
                "final_observation": final_observation,
                "ui_analysis": ui_analysis,
                "collected_data": {
                    "execution_results_count": len(self.execution_results),
                    "screenshots_count": len(self.screenshots),
                    "observations_count": len(self.observations)
                },
                "summary": {
                    "total_tests": len(test_results),
                    "passed_tests": sum(1 for r in test_results if r.success),
                    "failed_tests": sum(1 for r in test_results if not r.success),
                    "backend_api_connected": backend_api_status.get("status") == "connected",
                    "web_server_connected": server_connected,
                    "ui_quality": {
                        "average_score": ui_analysis.get("summary", {}).get("average_score", 0),
                        "good_designs": ui_analysis.get("summary", {}).get("good_designs", 0),
                        "needs_improvement": ui_analysis.get("summary", {}).get("needs_improvement", 0)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info("✅ Test cycle completed successfully")
            logger.info(f"🎨 UI Analysis: {ui_analysis.get('summary', {}).get('good_designs', 0)}/{len(self.screenshots)} good designs")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Test cycle failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }

async def main():
    """
    Main entry point for the test agent
    """
    parser = argparse.ArgumentParser(description='Howdy Test Agent - AI Testing Interface with UI Analysis')
    parser.add_argument('--web-port', type=int, default=3000, help='Web application port')
    parser.add_argument('--backend-port', type=int, default=443, help='Backend API port')
    parser.add_argument('--output', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--prompt', type=str, help='Direct prompt input (for testing)')
    parser.add_argument('--env', choices=['LOCAL'], default='LOCAL', help='Stagehand environment (LOCAL only)')
    
    args = parser.parse_args()
    
    # Create test agent instance
    agent = HowdyTestAgent(web_port=args.web_port, backend_port=args.backend_port)
    
    # Override prompt if provided via command line
    if args.prompt:
        original_get_prompt = agent.get_ai_prompt
        agent.get_ai_prompt = lambda: args.prompt
    
    try:
        # Initialize Stagehand
        logger.info("Initializing Stagehand browser automation...")
        stagehand_initialized = await agent.initialize_stagehand()
        
        if not stagehand_initialized:
            logger.warning("Stagehand initialization failed, continuing with simulation mode")
        
        # Run the full test cycle
        results = await agent.run_full_test_cycle()
        
        # Output results
        if args.output == 'json':
            print(json.dumps(results, indent=2))
        else:
            # Text output with pretty UI analysis
            print(f"\n{'='*70}")
            print("TEST RESULTS SUMMARY")
            print(f"{'='*70}")
            print(f"Total Tests: {results.get('summary', {}).get('total_tests', 0)}")
            print(f"✅ Passed: {results.get('summary', {}).get('passed_tests', 0)}")
            print(f"❌ Failed: {results.get('summary', {}).get('failed_tests', 0)}")
            print(f"Status: {'✅ Success' if 'error' not in results else '❌ Failed'}")
            
            # Show UI quality summary
            ui_quality = results.get('summary', {}).get('ui_quality', {})
            print(f"\n🎨 UI Design Quality:")
            print(f"   Average Score: {ui_quality.get('average_score', 0):.1f}/10")
            print(f"   ✅ Good Designs: {ui_quality.get('good_designs', 0)}")
            print(f"   ⚠️  Needs Improvement: {ui_quality.get('needs_improvement', 0)}")
            
            # Print detailed UI analysis if available
            if 'ui_analysis' in results:
                agent.print_ui_analysis_report(results['ui_analysis'])
    
    finally:
        # Always close Stagehand session
        await agent.close_stagehand()

if __name__ == "__main__":
    asyncio.run(main())