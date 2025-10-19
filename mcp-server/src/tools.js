/**
 * MCP Tool Definitions for Lumen Browser Testing
 * Defines all available tools that can be called by AI assistants
 */

export const tools = [
  {
    name: 'run_browser_test',
    description: 'Execute a single browser test action using AI-powered Observe + Act pattern. The AI will observe the page to identify elements, then execute the action. Perfect for testing specific user interactions like clicking buttons, filling forms, or navigating pages.',
    inputSchema: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'Target website URL to test (must include http:// or https://)'
        },
        test: {
          type: 'string',
          description: 'Natural language description of the test to perform (e.g., "click the login button", "fill out the contact form", "navigate to pricing page")'
        },
        captureScreenshots: {
          type: 'boolean',
          description: 'Whether to capture screenshots during the test for visual analysis',
          default: false
        },
        analyzeUI: {
          type: 'boolean',
          description: 'Whether to run AI visual analysis on captured screenshots (requires captureScreenshots to be true)',
          default: false
        }
      },
      required: ['url', 'test']
    }
  },
  {
    name: 'run_agent_test',
    description: 'Execute a multi-step autonomous browser test using Computer Use (CU) Agent mode. The AI agent will autonomously navigate and interact with the website to complete complex workflows. Best for testing complete user journeys like signup flows, checkout processes, or multi-page workflows.',
    inputSchema: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'Starting URL for the test'
        },
        test: {
          type: 'string',
          description: 'High-level description of the workflow to test (e.g., "sign up for an account and verify email", "add item to cart and complete checkout")'
        },
        captureScreenshots: {
          type: 'boolean',
          description: 'Whether to capture screenshots at each step',
          default: true
        },
        analyzeUI: {
          type: 'boolean',
          description: 'Whether to run AI visual analysis on the workflow',
          default: false
        }
      },
      required: ['url', 'test']
    }
  },
  {
    name: 'analyze_screenshot',
    description: 'Analyze a UI screenshot using vision AI models to critique design, UX, accessibility, and visual quality. Provides detailed feedback on what works well and what could be improved.',
    inputSchema: {
      type: 'object',
      properties: {
        screenshotPath: {
          type: 'string',
          description: 'Absolute file path to the screenshot image to analyze'
        }
      },
      required: ['screenshotPath']
    }
  },
  {
    name: 'get_test_results',
    description: 'Retrieve detailed results from a previous test run, including screenshots, test execution details, and AI analysis if available.',
    inputSchema: {
      type: 'object',
      properties: {
        runId: {
          type: 'string',
          description: 'The unique run ID from a previous test (optional - if not provided, returns the most recent test)'
        }
      },
      required: []
    }
  },
  {
    name: 'list_test_runs',
    description: 'List all test runs that have been executed, with summary information about each run.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  }
];

/**
 * Get tool by name
 */
export function getTool(name) {
  return tools.find(tool => tool.name === name);
}

/**
 * Validate tool arguments against schema
 */
export function validateToolArguments(toolName, args) {
  const tool = getTool(toolName);
  if (!tool) {
    throw new Error(`Tool '${toolName}' not found`);
  }

  const schema = tool.inputSchema;
  const errors = [];

  // Check required fields
  if (schema.required) {
    for (const field of schema.required) {
      if (!(field in args)) {
        errors.push(`Missing required field: ${field}`);
      }
    }
  }

  // Basic type checking
  for (const [key, value] of Object.entries(args)) {
    if (schema.properties[key]) {
      const expectedType = schema.properties[key].type;
      const actualType = typeof value;
      
      if (expectedType === 'boolean' && actualType !== 'boolean') {
        errors.push(`Field '${key}' should be boolean, got ${actualType}`);
      } else if (expectedType === 'string' && actualType !== 'string') {
        errors.push(`Field '${key}' should be string, got ${actualType}`);
      } else if (expectedType === 'number' && actualType !== 'number') {
        errors.push(`Field '${key}' should be number, got ${actualType}`);
      }
    }
  }

  if (errors.length > 0) {
    throw new Error(`Validation errors: ${errors.join(', ')}`);
  }

  return true;
}
