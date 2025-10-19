/**
 * MCP Resource Handlers for Lumen Browser Testing
 * Provides access to test run data, screenshots, and analysis results
 */

import fs from 'fs/promises';
import path from 'path';

/**
 * Resource template definitions
 */
export const resourceTemplates = [
  {
    uriTemplate: 'test-run://{runId}',
    name: 'Test Run Results',
    description: 'Access complete test run data including execution details, screenshots, and AI analysis',
    mimeType: 'application/json'
  },
  {
    uriTemplate: 'screenshot://{runId}/{step}',
    name: 'Test Screenshot',
    description: 'Access individual screenshot from a test run',
    mimeType: 'image/png'
  },
  {
    uriTemplate: 'test-runs://list',
    name: 'All Test Runs',
    description: 'List all available test runs with summary information',
    mimeType: 'application/json'
  }
];

/**
 * Parse resource URI
 */
function parseResourceUri(uri) {
  const match = uri.match(/^(\w+):\/\/(.+)$/);
  if (!match) {
    throw new Error(`Invalid resource URI: ${uri}`);
  }

  const [, scheme, path] = match;
  return { scheme, path };
}

/**
 * Get test run resource
 */
export async function getTestRunResource(runId, browserManager) {
  const testRun = browserManager.getTestResults(runId);
  
  if (!testRun) {
    throw new Error(`Test run not found: ${runId}`);
  }

  // Return sanitized test run data (without large base64 images)
  const sanitized = {
    ...testRun,
    screenshots: testRun.screenshots?.map(s => ({
      filename: s.filename,
      filepath: s.filepath,
      step: s.step,
      prefix: s.prefix,
      timestamp: s.timestamp,
      url: s.url
      // Exclude base64Image to keep response size manageable
    }))
  };

  return {
    uri: `test-run://${runId}`,
    mimeType: 'application/json',
    text: JSON.stringify(sanitized, null, 2)
  };
}

/**
 * Get screenshot resource
 */
export async function getScreenshotResource(runId, step, browserManager) {
  const testRun = browserManager.getTestResults(runId);
  
  if (!testRun) {
    throw new Error(`Test run not found: ${runId}`);
  }

  if (!testRun.screenshots || testRun.screenshots.length === 0) {
    throw new Error(`No screenshots available for run: ${runId}`);
  }

  const screenshot = testRun.screenshots.find(s => s.step === parseInt(step));
  
  if (!screenshot) {
    throw new Error(`Screenshot not found: step ${step} in run ${runId}`);
  }

  // Read the screenshot file
  try {
    const imageBuffer = await fs.readFile(screenshot.filepath);
    const base64Image = imageBuffer.toString('base64');

    return {
      uri: `screenshot://${runId}/${step}`,
      mimeType: 'image/png',
      blob: base64Image
    };
  } catch (error) {
    throw new Error(`Failed to read screenshot: ${error.message}`);
  }
}

/**
 * List all test runs
 */
export async function listTestRunsResource(browserManager) {
  const allRuns = browserManager.getAllTestResults();
  
  // Return summary information
  const summary = allRuns.map(run => ({
    runId: run.runId,
    url: run.url,
    test: run.test,
    mode: run.mode,
    success: run.success,
    startTime: run.startTime,
    endTime: run.endTime,
    screenshotCount: run.screenshots?.length || 0,
    hasAnalysis: !!run.analysis
  }));

  return {
    uri: 'test-runs://list',
    mimeType: 'application/json',
    text: JSON.stringify({
      totalRuns: summary.length,
      runs: summary
    }, null, 2)
  };
}

/**
 * Main resource handler
 */
export async function handleResourceRequest(uri, browserManager) {
  const { scheme, path } = parseResourceUri(uri);

  switch (scheme) {
    case 'test-run': {
      const runId = path;
      return await getTestRunResource(runId, browserManager);
    }

    case 'screenshot': {
      const [runId, step] = path.split('/');
      return await getScreenshotResource(runId, step, browserManager);
    }

    case 'test-runs': {
      if (path === 'list') {
        return await listTestRunsResource(browserManager);
      }
      throw new Error(`Unknown test-runs path: ${path}`);
    }

    default:
      throw new Error(`Unknown resource scheme: ${scheme}`);
  }
}

/**
 * List available resources for a test run
 */
export function listResourcesForRun(testRun) {
  const resources = [
    {
      uri: `test-run://${testRun.runId}`,
      name: `Test Run: ${testRun.test}`,
      description: `Results from ${testRun.mode} test on ${testRun.url}`,
      mimeType: 'application/json'
    }
  ];

  // Add screenshot resources
  if (testRun.screenshots && testRun.screenshots.length > 0) {
    testRun.screenshots.forEach(screenshot => {
      resources.push({
        uri: `screenshot://${testRun.runId}/${screenshot.step}`,
        name: `Screenshot: ${screenshot.filename}`,
        description: `Screenshot from step ${screenshot.step}`,
        mimeType: 'image/png'
      });
    });
  }

  return resources;
}
