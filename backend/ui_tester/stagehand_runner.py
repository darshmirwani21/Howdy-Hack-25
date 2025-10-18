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
from stagehand import Stagehand, StagehandConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StagehandRunner:
    """Main class for running Stagehand with OpenRouter backend."""
    
    def __init__(self, headless: bool = False, slowmo: int = 0):
        self.headless = headless
        self.slowmo = slowmo
        self.stagehand: Optional[Stagehand] = None
        
    async def initialize(self) -> None:
        """Initialize Stagehand with OpenRouter configuration."""
        try:
            # Validate required environment variables
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")
            
            # Get model configuration
            model_name = os.getenv('STAGEHAND_MODEL', 'tngtech/deepseek-r1t-chimera:free')
            openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
            
            logger.info(f"Initializing Stagehand with model: {model_name}")
            logger.info(f"OpenRouter base URL: {openrouter_base_url}")
            
            # Configure Stagehand
            config = StagehandConfig(
                env="LOCAL",  # Use local Playwright
                model_name=model_name,
                model_client_options={
                    "apiKey": openrouter_api_key,
                    "baseURL": openrouter_base_url
                },
                headless=self.headless,
                slowmo=self.slowmo,
                verbose=1
            )
            
            # Initialize Stagehand
            self.stagehand = Stagehand(config=config)
            await self.stagehand.init()
            
            logger.info(f"Stagehand initialized successfully")
            logger.info(f"Session ID: {self.stagehand.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Stagehand: {e}")
            raise
    
    async def execute_instructions(self, instructions: List[str], base_url: str = None) -> None:
        """Execute a list of natural language instructions."""
        if not self.stagehand:
            raise RuntimeError("Stagehand not initialized. Call initialize() first.")
        
        page = self.stagehand.page
        
        try:
            # Navigate to base URL if provided
            if base_url:
                logger.info(f"Navigating to: {base_url}")
                await page.goto(base_url)
            
            # Execute each instruction
            for i, instruction in enumerate(instructions, 1):
                instruction = instruction.strip()
                if not instruction:
                    continue
                    
                logger.info(f"Step {i}: {instruction}")
                
                try:
                    # Use Stagehand's act method for natural language actions
                    await page.act(instruction)
                    logger.info(f"✓ Step {i} completed successfully")
                    
                except Exception as e:
                    logger.error(f"✗ Step {i} failed: {e}")
                    # Continue with next instruction instead of stopping
                    continue
                    
        except Exception as e:
            logger.error(f"Error executing instructions: {e}")
            raise
    
    async def close(self) -> None:
        """Close the Stagehand session."""
        if self.stagehand:
            await self.stagehand.close()
            logger.info("Stagehand session closed")


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
