#!/usr/bin/env node

/**
 * Lumen MCP Server
 * AI-powered browser testing via Model Context Protocol
 * 
 * This MCP server exposes Lumen's browser testing capabilities to AI assistants,
 * allowing them to run automated browser tests, capture screenshots, and analyze UI/UX.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

import dotenv from 'dotenv';
import { BrowserTestManager } from './browser-manager.js';
import { tools, validateToolArguments } from './tools.js';
import { resourceTemplates, handleResourceRequest, listResourcesForRun } from './resources.js';

// Load environment variables
dotenv.config();

// Global browser manager instance
const browserManager = new BrowserTestManager();

// Create MCP server
const server = new Server(
  {
    name: 'lumen-browser-testing',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {},
      resources: {}
    }
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

/**
 * Handle tool execution
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    // Validate arguments
    validateToolArguments(name, args || {});

    // Get API key from environment
    const openrouterApiKey = process.env.OPENROUTER_API_KEY;
    if (!openrouterApiKey) {
      return {
        content: [
          {
            type: 'text',
            text: 'Error: OPENROUTER_API_KEY environment variable is not set. Please configure it in your .env file.'
          }
        ],
        isError: true
      };
    }

    // Route to appropriate handler
    switch (name) {
      case 'run_browser_test':
        return await handleRunBrowserTest(args, openrouterApiKey);

      case 'run_agent_test':
        return await handleRunAgentTest(args, openrouterApiKey);

      case 'analyze_screenshot':
        return await handleAnalyzeScreenshot(args, openrouterApiKey);

      case 'get_test_results':
        return await handleGetTestResults(args);

      case 'list_test_runs':
        return await handleListTestRuns();

      default:
        return {
          content: [
            {
              type: 'text',
              text: `Unknown tool: ${name}`
            }
          ],
          isError: true
        };
    }
  } catch (error) {
    console.error(`Error executing tool ${name}:`, error);
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

/**
 * List available resources
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const resources = [...resourceTemplates];

  // Add resources for all test runs
  const allRuns = browserManager.getAllTestResults();
  allRuns.forEach(run => {
    resources.push(...listResourcesForRun(run));
  });

  return { resources };
});

/**
 * Read resource content
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  try {
    const resource = await handleResourceRequest(uri, browserManager);
    return {
      contents: [resource]
    };
  } catch (error) {
    console.error(`Error reading resource ${uri}:`, error);
    throw error;
  }
});

/**
 * Tool Handlers
 */

async function handleRunBrowserTest(args, openrouterApiKey) {
  const { url, test, captureScreenshots = false, analyzeUI = false } = args;

  console.error(`\n🧪 Running browser test: "${test}" on ${url}`);

  try {
    const testRun = await browserManager.runTest(url, test, {
      captureScreenshots,
      useAgent: false,
      openrouterApiKey,
      analyzeUI
    });

    // Format response
    let response = `# Browser Test Results\n\n`;
    response += `**URL**: ${testRun.url}\n`;
    response += `**Test**: ${testRun.test}\n`;
    response += `**Status**: ${testRun.success ? '✅ SUCCESS' : '❌ FAILED'}\n`;
    response += `**Mode**: ${testRun.mode}\n`;
    response += `**Run ID**: ${testRun.runId}\n\n`;

    // Test results
    if (testRun.testResults) {
      response += `## Test Execution\n\n`;
      if (testRun.testResults.observations) {
        response += `**Observations**: ${testRun.testResults.observations.length} action(s) identified\n`;
      }
      if (testRun.testResults.actions) {
        response += `**Actions Executed**: ${testRun.testResults.actions.length}\n`;
        testRun.testResults.actions.forEach((action, i) => {
          response += `  ${i + 1}. ${action.description} - ${action.success ? '✅' : '❌'}\n`;
        });
      }
    }

    // Screenshots
    if (testRun.screenshots && testRun.screenshots.length > 0) {
      response += `\n## Screenshots\n\n`;
      response += `Captured ${testRun.screenshots.length} screenshot(s)\n`;
      response += `Access via: \`screenshot://${testRun.runId}/{step}\`\n`;
    }

    // Analysis
    if (testRun.analysis) {
      if (testRun.analysis.visionCritique) {
        response += `\n## Visual Analysis\n\n${testRun.analysis.visionCritique}\n`;
      }
      if (testRun.analysis.summary) {
        response += `\n## Summary\n\n${testRun.analysis.summary}\n`;
      }
    }

    // Errors
    if (testRun.error) {
      response += `\n## Error\n\n${testRun.error}\n`;
    }

    return {
      content: [
        {
          type: 'text',
          text: response
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Test execution failed: ${error.message}`
        }
      ],
      isError: true
    };
  }
}

async function handleRunAgentTest(args, openrouterApiKey) {
  const { url, test, captureScreenshots = true, analyzeUI = false } = args;

  console.error(`\n🤖 Running agent test: "${test}" on ${url}`);

  try {
    const testRun = await browserManager.runTest(url, test, {
      captureScreenshots,
      useAgent: true,
      openrouterApiKey,
      analyzeUI
    });

    // Format response
    let response = `# Agent Test Results\n\n`;
    response += `**URL**: ${testRun.url}\n`;
    response += `**Test**: ${testRun.test}\n`;
    response += `**Status**: ${testRun.success ? '✅ SUCCESS' : '❌ FAILED'}\n`;
    response += `**Mode**: Computer Use Agent\n`;
    response += `**Run ID**: ${testRun.runId}\n\n`;

    // Agent results
    if (testRun.testResults && testRun.testResults.result) {
      response += `## Agent Result\n\n${JSON.stringify(testRun.testResults.result, null, 2)}\n`;
    }

    // Screenshots
    if (testRun.screenshots && testRun.screenshots.length > 0) {
      response += `\n## Screenshots\n\n`;
      response += `Captured ${testRun.screenshots.length} screenshot(s) during workflow\n`;
    }

    // Analysis
    if (testRun.analysis) {
      if (testRun.analysis.visionCritique) {
        response += `\n## Visual Analysis\n\n${testRun.analysis.visionCritique}\n`;
      }
      if (testRun.analysis.summary) {
        response += `\n## Summary\n\n${testRun.analysis.summary}\n`;
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: response
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Agent test failed: ${error.message}`
        }
      ],
      isError: true
    };
  }
}

async function handleAnalyzeScreenshot(args, openrouterApiKey) {
  const { screenshotPath } = args;

  console.error(`\n🔍 Analyzing screenshot: ${screenshotPath}`);

  try {
    const critique = await browserManager.critiqueScreenshot(screenshotPath, openrouterApiKey);

    return {
      content: [
        {
          type: 'text',
          text: `# Screenshot Analysis\n\n${critique}`
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Screenshot analysis failed: ${error.message}`
        }
      ],
      isError: true
    };
  }
}

async function handleGetTestResults(args) {
  const { runId } = args;

  try {
    let testRun;
    if (runId) {
      testRun = browserManager.getTestResults(runId);
      if (!testRun) {
        return {
          content: [
            {
              type: 'text',
              text: `Test run not found: ${runId}`
            }
          ],
          isError: true
        };
      }
    } else {
      testRun = browserManager.getCurrentRun();
      if (!testRun) {
        return {
          content: [
            {
              type: 'text',
              text: 'No test runs available'
            }
          ],
          isError: true
        };
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(testRun, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Failed to get test results: ${error.message}`
        }
      ],
      isError: true
    };
  }
}

async function handleListTestRuns() {
  try {
    const allRuns = browserManager.getAllTestResults();
    
    let response = `# Test Runs (${allRuns.length})\n\n`;
    
    if (allRuns.length === 0) {
      response += 'No test runs yet.\n';
    } else {
      allRuns.forEach((run, i) => {
        response += `## ${i + 1}. ${run.test}\n`;
        response += `- **Run ID**: ${run.runId}\n`;
        response += `- **URL**: ${run.url}\n`;
        response += `- **Status**: ${run.success ? '✅ Success' : '❌ Failed'}\n`;
        response += `- **Mode**: ${run.mode}\n`;
        response += `- **Time**: ${run.startTime}\n`;
        if (run.screenshots) {
          response += `- **Screenshots**: ${run.screenshots.length}\n`;
        }
        response += '\n';
      });
    }

    return {
      content: [
        {
          type: 'text',
          text: response
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Failed to list test runs: ${error.message}`
        }
      ],
      isError: true
    };
  }
}

/**
 * Cleanup on exit
 */
process.on('SIGINT', async () => {
  console.error('\n🛑 Shutting down...');
  await browserManager.cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.error('\n🛑 Shutting down...');
  await browserManager.cleanup();
  process.exit(0);
});

/**
 * Start the server
 */
async function main() {
  console.error('🚀 Starting Lumen MCP Server...');
  console.error('📋 Available tools: run_browser_test, run_agent_test, analyze_screenshot, get_test_results, list_test_runs');
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('✅ Lumen MCP Server running');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
