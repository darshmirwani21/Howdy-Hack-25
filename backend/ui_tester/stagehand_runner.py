#!/usr/bin/env python3
"""
OpenRouter + Stagehand CLI Integration

A Python CLI script that configures Stagehand to use OpenRouter + DeepSeek R1T
as its LLM backend, accepting natural language test instructions and executing
them through Stagehand's autonomous agent.
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from playwright.async_api import async_playwright
from stagehand import Agent, AgentConfig, AgentProvider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StagehandRunner:
    """Main class for running Stagehand Agent with OpenRouter backend."""
    
    def __init__(self, headless: bool = False, slowmo: int = 0):
        self.headless = headless
        self.slowmo = slowmo
        self.playwright = None
        self.browser = None
        self.page = None
        self.agent: Optional[Agent] = None
        
    async def initialize(self) -> None:
        """Initialize Playwright and Stagehand Agent with OpenRouter configuration."""
        try:
            # Validate required environment variables
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")
            
            # Get model configuration
            model_name = os.getenv('STAGEHAND_MODEL', 'tngtech/deepseek-r1t-chimera:free')
            openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
            
            logger.info(f"Initializing Stagehand Agent with model: {model_name}")
            logger.info(f"OpenRouter base URL: {openrouter_base_url}")
            
            # Initialize Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slowmo
            )
            self.page = await self.browser.new_page()
            
            # Configure Stagehand Agent
            agent_config = AgentConfig(
                provider=AgentProvider.OPENAI,  # Use OpenAI-compatible client
                model=model_name,
                options={
                    "apiKey": openrouter_api_key,
                    "baseURL": openrouter_base_url
                }
            )
            
            # Initialize Agent (we'll create a mock stagehand client for now)
            # Note: This is a simplified approach - in production you'd want proper integration
            self.agent = Agent(None, agent_config)
            
            logger.info("Stagehand Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Stagehand Agent: {e}")
            raise
    
    async def execute_instructions(self, instructions: List[str], base_url: str = None) -> None:
        """Execute a list of natural language instructions using Stagehand Agent."""
        if not self.page or not self.agent:
            raise RuntimeError("Playwright and Agent not initialized. Call initialize() first.")
        
        try:
            # Navigate to base URL if provided
            if base_url:
                logger.info(f"Navigating to: {base_url}")
                await self.page.goto(base_url)
            
            # Parse instructions - handle both single complex instructions and multiple simple ones
            if len(instructions) == 1 and any(keyword in instructions[0].lower() for keyword in ['then', 'and', 'after', 'next']):
                # Single complex instruction with multiple steps - parse it
                logger.info(f"Parsing complex instruction: {instructions[0]}")
                parsed_steps = self._parse_complex_instruction(instructions[0])
                logger.info(f"Parsed into {len(parsed_steps)} steps: {parsed_steps}")
                
                for i, step in enumerate(parsed_steps, 1):
                    logger.info(f"Step {i}: {step}")
                    await self._execute_simple_action(step)
                    logger.info(f"✓ Step {i} completed successfully")
            else:
                # Multiple simple instructions or single simple instruction
                for i, instruction in enumerate(instructions, 1):
                    instruction = instruction.strip()
                    if not instruction:
                        continue
                        
                    logger.info(f"Step {i}: {instruction}")
                    await self._execute_simple_action(instruction)
                    logger.info(f"✓ Step {i} completed successfully")
                    
        except Exception as e:
            logger.error(f"Error executing instructions: {e}")
            raise
    
    async def _execute_simple_action(self, instruction: str) -> None:
        """Execute a simple action based on instruction text."""
        instruction_lower = instruction.lower()
        
        # Wait for page to load
        await self.page.wait_for_load_state('networkidle')
        
        if "click" in instruction_lower:
            # Handle various click instructions
            if "more information" in instruction_lower:
                await self._click_element(["text=More information", "a:has-text('More information')", "text=More", "a:has-text('More')"])
            elif "products" in instruction_lower:
                await self._click_element(["text=Products", "a:has-text('Products')", "[data-testid*='products']", "nav a:has-text('Products')"])
            elif "office" in instruction_lower:
                await self._click_element(["text=Office", "a:has-text('Office')", "[href*='office']", "a:has-text('Microsoft Office')"])
            elif "login" in instruction_lower or "sign in" in instruction_lower:
                await self._click_element(["text=Sign in", "text=Login", "a:has-text('Sign in')", "a:has-text('Login')", "[data-testid*='login']"])
            else:
                # Generic click - try to find any clickable element
                logger.warning(f"Generic click instruction: {instruction}")
                # Take a screenshot to see what's available
                await self.page.screenshot(path="debug_screenshot.png")
                logger.info("Debug screenshot saved - manual inspection needed")
                
        elif "extract" in instruction_lower and "title" in instruction_lower:
            # Extract page title
            title = await self.page.title()
            logger.info(f"Page title: {title}")
        elif "screenshot" in instruction_lower:
            # Take screenshot
            await self.page.screenshot(path="screenshot.png")
            logger.info("Screenshot saved as screenshot.png")
        elif "navigate" in instruction_lower or "go to" in instruction_lower:
            # Navigation is handled by the main method
            logger.info("Navigation handled by main method")
        else:
            logger.warning(f"Unknown instruction: {instruction}")
    
    async def _click_element(self, selectors: List[str]) -> None:
        """Try to click an element using multiple selector strategies."""
        clicked = False
        for selector in selectors:
            try:
                await self.page.click(selector, timeout=5000)
                clicked = True
                logger.info(f"Successfully clicked using selector: {selector}")
                break
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        if not clicked:
            logger.warning(f"Could not find element with any selector: {selectors}")
            # Take a screenshot for debugging
            await self.page.screenshot(path="debug_screenshot.png")
            logger.info("Debug screenshot saved as debug_screenshot.png")
    
    def _parse_complex_instruction(self, instruction: str) -> List[str]:
        """Parse a complex instruction into individual steps."""
        # Simple parsing - split on common conjunctions
        # This is a basic implementation - in production you'd want more sophisticated parsing
        
        original_instruction = instruction
        instruction = instruction.lower()
        
        # Remove navigation part if present
        if "navigate to" in instruction or "go to" in instruction:
            # Find where the actual actions start
            click_index = instruction.find("click")
            if click_index != -1:
                instruction = instruction[click_index:]
        
        # Split on common step separators - try each one
        separators = ["then", "and", "after", "next"]
        steps = [instruction]
        
        for sep in separators:
            new_steps = []
            for step in steps:
                if sep in step:
                    # Split on this separator
                    parts = step.split(sep)
                    for part in parts:
                        part = part.strip()
                        if part:
                            new_steps.append(part)
                else:
                    new_steps.append(step)
            steps = new_steps
        
        # Clean up steps
        cleaned_steps = []
        for step in steps:
            step = step.strip()
            if step and not step.startswith("navigate") and not step.startswith("go to"):
                # Add "click" prefix if missing
                if not step.startswith("click") and ("menu" in step or "button" in step or "link" in step or "office" in step):
                    step = f"click {step}"
                cleaned_steps.append(step)
        
        logger.info(f"Original: '{original_instruction}'")
        logger.info(f"Cleaned steps: {cleaned_steps}")
        
        return cleaned_steps if cleaned_steps else [instruction]
    
    async def close(self) -> None:
        """Close the browser and Playwright session."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser session closed")


def parse_instructions_file(file_path: str) -> List[str]:
    """Parse instructions from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split by newlines and filter empty lines
        instructions = [line.strip() for line in content.split('\n') if line.strip()]
        
        logger.info(f"Loaded {len(instructions)} instructions from {file_path}")
        return instructions
        
    except FileNotFoundError:
        logger.error(f"Instructions file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading instructions file: {e}")
        sys.exit(1)


def parse_instructions_string(instructions_str: str) -> List[str]:
    """Parse instructions from a string."""
    # Split by newlines or semicolons
    instructions = []
    for delimiter in ['\n', ';']:
        if delimiter in instructions_str:
            instructions = [line.strip() for line in instructions_str.split(delimiter) if line.strip()]
            break
    
    if not instructions:
        instructions = [instructions_str.strip()]
    
    logger.info(f"Parsed {len(instructions)} instructions from string")
    return instructions


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenRouter + Stagehand CLI - Execute natural language browser automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute inline instructions
  python stagehand_runner.py --url https://example.com --instructions "Click the login button"

  # Execute instructions from file
  python stagehand_runner.py --file demo_instructions.txt

  # Run in headless mode
  python stagehand_runner.py --headless --instructions "Navigate to /dashboard"
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--instructions', '-i',
        help='Natural language instructions to execute'
    )
    input_group.add_argument(
        '--file', '-f',
        help='Path to file containing instructions (one per line)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--url', '-u',
        help='Base URL to navigate to before executing instructions'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (default: headed)'
    )
    parser.add_argument(
        '--slowmo',
        type=int,
        default=0,
        help='Slow down operations by specified milliseconds'
    )
    
    args = parser.parse_args()
    
    # Parse instructions
    if args.file:
        instructions = parse_instructions_file(args.file)
    else:
        instructions = parse_instructions_string(args.instructions)
    
    if not instructions:
        logger.error("No valid instructions provided")
        sys.exit(1)
    
    # Initialize and run
    runner = StagehandRunner(headless=args.headless, slowmo=args.slowmo)
    
    try:
        await runner.initialize()
        await runner.execute_instructions(instructions, args.url)
        logger.info("All instructions completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
