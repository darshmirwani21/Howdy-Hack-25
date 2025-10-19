#!/usr/bin/env python3
"""
Howdy Test Agent - Frontend Interface
Core Python file that AI agents call to perform automated testing
"""

import asyncio
import json
import sys
import argparse
import requests
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from stagehand import Stagehand
from stagehand.config import StagehandConfig
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
    Main test agent class that interfaces with Stagehand and AI agents
    
    This frontend class handles:
    1. Stagehand initialization and configuration (LOCAL mode)
    2. Getting prompts from LLM
    3. Connecting to the web port
    4. Making stagehand.agent() calls
    5. Using stagehand.observe() method
    
    Backend handles all actual test execution and logic
    """
    
    def __init__(self, web_port: int = 3000, backend_port: int = 443):
        self.web_port = web_port
        self.backend_port = backend_port
        self.base_url = f"http://localhost:{web_port}"
        self.backend_url = f"http://localhost:{backend_port}"
        self.stagehand = None
        self.page = None
        
        # Storage for execution results (Approach 5)
        self.execution_results = []  # Store all agent execution results
        self.screenshots = []         # Store screenshot paths
        self.observations = []        # Store observation results
        
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
            config = StagehandConfig(
               env="LOCAL",
               api_key="dummy-openai-key",
               model_name="openai/gpt-4",
               headless=False,
            )
            
            self.stagehand = Stagehand(config=config)
            
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
            # For hackathon: simulate AI prompt input
            # In production, this would connect to the AI agent API
            print("🤖 Waiting for AI agent prompt...")
            
            # Simulate getting prompt from stdin or API
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
        This is the core method that translates AI instructions into actionable tests
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
        This is where we translate natural language into Stagehand commands
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
        Stores results in memory for later backend analysis
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
            # API key and base URL are already configured in initialize_stagehand()
            agent = self.stagehand.agent({
                'provider': 'openai',
                'model': 'gpt-4o',
                'instructions': 'Execute web testing scenarios and report results'
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
                    screenshot_path = f"./screenshots/scenario_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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
        Replace this with actual Stagehand API calls
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
        Stores observation results in memory for later backend analysis
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
        Simple check that the web server is accessible
        """
        logger.info(f"Checking connection to web server on port {self.web_port}...")
        
        try:
            # Simple connection check
            response = requests.get(f"http://localhost:{self.web_port}", timeout=5)
            logger.info(f"✅ Web server connected on port {self.web_port}")
            return True
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️  Cannot connect to web server on port {self.web_port}")
            return False
        except Exception as e:
            logger.error(f"❌ Error connecting to web server: {e}")
            return False
    
    async def send_to_backend_for_analysis(self) -> Dict[str, Any]:
        """
        Send all collected execution data to backend for analysis
        This includes agent results, screenshots, and observations
        """
        logger.info("📤 Sending collected data to backend for analysis...")
        
        try:
            # Prepare payload with all collected data
            payload = {
                "execution_results": self.execution_results,
                "screenshot_paths": self.screenshots,
                "observations": self.observations,
                "metadata": {
                    "total_executions": len(self.execution_results),
                    "total_screenshots": len(self.screenshots),
                    "total_observations": len(self.observations),
                    "web_port": self.web_port,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info(f"Payload contains:")
            logger.info(f"  - {len(self.execution_results)} execution results")
            logger.info(f"  - {len(self.screenshots)} screenshots")
            logger.info(f"  - {len(self.observations)} observations")
            
            # Send to backend analysis endpoint
            response = requests.post(
                f"http://localhost:{self.backend_port}/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                analysis_result = response.json()
                logger.info("✅ Backend analysis completed successfully")
                return {
                    "status": "success",
                    "analysis": analysis_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Backend returned status code: {response.status_code}")
                return {
                    "status": "error",
                    "error": f"Backend returned {response.status_code}",
                    "response": response.text,
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to backend for analysis")
            return {
                "status": "error",
                "error": "Backend connection refused",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error sending data to backend: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_full_test_cycle(self) -> Dict[str, Any]:
        """
        Run the complete test cycle:
        1. Get AI prompt
        2. Process prompt into test scenarios
        3. Check backend API connection
        4. Verify web server connection
        5. Execute stagehand.agent() calls (stores results in memory)
        6. Run stagehand.observe() (stores observations in memory)
        7. Send all collected data to backend for analysis
        
        Returns final results including backend analysis
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
            
            # Step 7: Send all collected data to backend for analysis
            logger.info("📊 Sending data to backend for analysis...")
            backend_analysis = await self.send_to_backend_for_analysis()
            
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
                "backend_analysis": backend_analysis,  # Include backend analysis results
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
                    "backend_analysis_status": backend_analysis.get("status"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info("✅ Test cycle completed successfully")
            logger.info(f"📊 Backend analysis status: {backend_analysis.get('status')}")
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
    parser = argparse.ArgumentParser(description='Howdy Test Agent - AI Testing Interface')
    parser.add_argument('--web-port', type=int, default=3000, help='Web application port')
    parser.add_argument('--backend-port', type=int, default=443, help='Backend API port')
    parser.add_argument('--output', choices=['json', 'text'], default='json', help='Output format')
    parser.add_argument('--prompt', type=str, help='Direct prompt input (for testing)')
    parser.add_argument('--env', choices=['LOCAL'], default='LOCAL', help='Stagehand environment (LOCAL only)')
    
    args = parser.parse_args()
    
    # Create test agent instance
    agent = HowdyTestAgent(web_port=args.web_port, backend_port=args.backend_port)
    
    # Override prompt if provided via command line
    if args.prompt:
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
            print(f"Test Results Summary:")
            print(f"Total Tests: {results.get('summary', {}).get('total_tests', 0)}")
            print(f"Passed: {results.get('summary', {}).get('passed_tests', 0)}")
            print(f"Failed: {results.get('summary', {}).get('failed_tests', 0)}")
            print(f"Status: {'✅ Success' if 'error' not in results else '❌ Failed'}")
    
    finally:
        # Always close Stagehand session
        await agent.close_stagehand()

if __name__ == "__main__":
    asyncio.run(main())
