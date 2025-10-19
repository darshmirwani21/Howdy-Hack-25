#!/usr/bin/env node
/**
 * Stagehand Browser Automation Runner with Visual UI Testing
 * 
 * CLI tool for AI-powered browser testing with screenshot capture and AI analysis
 * 
 * Usage: node runner.js --url <URL> --test "<test description>" [--agent] [--screenshots]
 */

import { Stagehand } from '@browserbasehq/stagehand';
import dotenv from 'dotenv';
import { parseArgs } from 'node:util';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config();

// Console output capture
let terminalOutput = [];
const originalConsole = {
  log: console.log,
  error: console.error,
  warn: console.warn,
  info: console.info
};

function captureConsoleOutput() {
  ['log', 'error', 'warn', 'info'].forEach(method => {
    console[method] = (...args) => {
      const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
      ).join(' ');
      terminalOutput.push(message);
      originalConsole[method](...args);
    };
  });
}

function restoreConsole() {
  Object.assign(console, originalConsole);
}

// Parse command line arguments
function parseArguments() {
  const { values } = parseArgs({
    options: {
      url: {
        type: 'string',
        short: 'u'
      },
      test: {
        type: 'string',
        short: 't'
      },
      agent: {
        type: 'boolean',
        short: 'a',
        default: false
      },
      screenshots: {
        type: 'boolean',
        short: 's',
        default: false
      }
    }
  });

  if (!values.url || !values.test) {
    console.error('❌ Error: Both --url and --test arguments are required\n');
    console.log('Usage: node runner.js --url <URL> --test "<test description>" [--agent] [--screenshots]\n');
    console.log('Examples:');
    console.log('  node runner.js --url https://example.com --test "Click the login button"');
    console.log('  node runner.js --url https://example.com --test "Navigate to pricing" --agent --screenshots\n');
    process.exit(1);
  }

  return {
    url: values.url,
    test: values.test,
    useAgent: values.agent,
    captureScreenshots: values.screenshots
  };
}

// Create timestamped run folder
async function createRunFolder() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').split('.')[0];
  const runFolder = path.join(__dirname, 'screenshots', `run_${timestamp}`);
  await fs.mkdir(runFolder, { recursive: true });
  return runFolder;
}

// Save screenshot
async function saveScreenshot(page, runFolder, prefix, stepNumber) {
  const filename = `${prefix}_step${stepNumber}.png`;
  const filepath = path.join(runFolder, filename);
  
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`📸 Screenshot saved: ${filename}`);
  return { filepath, filename };
}

// Save terminal output to file
async function saveTerminalOutput(runFolder, output) {
  const filepath = path.join(runFolder, 'terminal_output.txt');
  await fs.writeFile(filepath, output.join('\n'), 'utf-8');
  console.log(`📝 Terminal output saved: terminal_output.txt`);
}

// Vision Model Analysis - All screenshots in one call
async function analyzeScreenshotsWithVision(screenshotPaths, openrouterApiKey) {
  try {
    console.log('\n🔍 Running vision model analysis on all screenshots...');
    
    // Read all screenshots and convert to base64
    const imageContents = [];
    for (const screenshotPath of screenshotPaths) {
      const imageBuffer = await fs.readFile(screenshotPath);
      const base64Image = imageBuffer.toString('base64');
      imageContents.push({
        type: 'image_url',
        image_url: {
          url: `data:image/png;base64,${base64Image}`
        }
      });
    }
    
    // Create message content with prompt and all images
    const messageContent = [
      {
        type: 'text',
        text: 'critique this UI. if it is good, just say its good'
      },
      ...imageContents
    ];
    
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openrouterApiKey}`,
        'HTTP-Referer': 'https://github.com/browserbase/stagehand',
        'X-Title': 'Stagehand UI Analysis'
      },
      body: JSON.stringify({
        model: 'openai/gpt-4o',
        messages: [
          {
            role: 'user',
            content: messageContent
          }
        ],
        max_tokens: 1000
      })
    });

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error.message || JSON.stringify(data.error));
    }
    
    return data.choices[0].message.content;
  } catch (error) {
    console.error('⚠️  Failed to get vision model critique:', error.message);
    return 'Vision model analysis failed: ' + error.message;
  }
}

// Summary Analysis with GPT-4o-mini
async function generateSummary(visionCritique, terminalOutput, openrouterApiKey) {
  try {
    console.log('🔍 Generating summary with GPT-4o-mini...\n');
    
    const prompt = `You are analyzing browser testing results. Based on the screenshot feedback and terminal output, summarize what's wrong and what can be improved. If it's actually good, say that.

SCREENSHOT FEEDBACK:
${visionCritique}

TERMINAL OUTPUT:
${terminalOutput.join('\n')}`;

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openrouterApiKey}`,
        'HTTP-Referer': 'https://github.com/browserbase/stagehand',
        'X-Title': 'Stagehand Test Summary'
      },
      body: JSON.stringify({
        model: 'openai/gpt-4o-mini',
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 800
      })
    });

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error.message || JSON.stringify(data.error));
    }
    
    return data.choices[0].message.content;
  } catch (error) {
    console.error('⚠️  Failed to generate summary:', error.message);
    return 'Summary generation failed: ' + error.message;
  }
}

async function runTest() {
  const { url, test, useAgent, captureScreenshots } = parseArguments();

  // Validate environment variables
  const openrouterApiKey = process.env.OPENROUTER_API_KEY;
  const modelName = process.env.STAGEHAND_MODEL || 'openai/gpt-4o-mini';

  if (!openrouterApiKey) {
    console.error('❌ Error: OPENROUTER_API_KEY environment variable is required');
    console.error('Please set it in your .env file or environment\n');
    process.exit(1);
  }

  // Start capturing console output
  captureConsoleOutput();

  // Setup run folder if screenshots enabled
  let runFolder = null;
  let screenshotPaths = [];
  let stepCounter = 0;
  
  if (captureScreenshots) {
    runFolder = await createRunFolder();
    console.log(`📁 Run folder created: ${runFolder}\n`);
  }

  console.log('🚀 Starting Stagehand Browser Automation');
  console.log('=' .repeat(80));
  console.log(`🌐 Target URL: ${url}`);
  console.log(`🧪 Test: ${test}`);
  console.log(`🤖 Model: ${modelName}`);
  console.log(`🎯 Mode: ${useAgent ? 'Computer Use Agent (CU)' : 'Normal (single action)'}`);
  console.log(`📸 Screenshots: ${captureScreenshots ? 'Enabled' : 'Disabled'}`);
  console.log('=' .repeat(80));

  // Initialize Stagehand with LOCAL environment
  const stagehand = new Stagehand({
    env: 'LOCAL',
    headless: false,
    verbose: 1,
    debugDom: true,
    enableCaching: false,
    modelName: modelName,
    modelClientOptions: {
      apiKey: openrouterApiKey,
      baseURL: 'https://openrouter.ai/api/v1',
      defaultHeaders: {
        'HTTP-Referer': 'https://github.com/browserbase/stagehand',
        'X-Title': 'Stagehand Automation'
      }
    }
  });

  try {
    // Initialize Stagehand
    console.log('\n🔧 Initializing Stagehand...');
    await stagehand.init();
    console.log('✅ Stagehand initialized\n');

    // Navigate to URL
    console.log(`🌐 Navigating to ${url}...`);
    await stagehand.page.goto(url);
    console.log('✅ Page loaded\n');

    // Capture "before" screenshot
    if (captureScreenshots) {
      stepCounter++;
      console.log('📸 Capturing BEFORE screenshot...');
      const { filepath } = await saveScreenshot(stagehand.page, runFolder, 'before', stepCounter);
      screenshotPaths.push(filepath);
    }

    // Run the test
    if (useAgent) {
      // Computer Use (CU) Agent Mode - Multi-step autonomous
      console.log('🤖 Starting Computer Use Agent (multi-step autonomous)...');
      console.log('-'.repeat(80));
      
      const agent = stagehand.agent({
        model: modelName
      });
      
      const result = await agent.execute(test);
      
      console.log('-'.repeat(80));
      console.log('✅ Computer Use Agent completed!\n');
      console.log('📊 Result:', result);
    } else {
      // Normal Mode - Single action
      console.log('🤖 Starting single action (normal mode)...');
      console.log('-'.repeat(80));
      
      const page = stagehand.page;
      await page.act(test);

      console.log('-'.repeat(80));
      console.log('✅ Action completed!\n');
    }

    // Capture "after" screenshot
    if (captureScreenshots) {
      stepCounter++;
      console.log('📸 Capturing AFTER screenshot...');
      const { filepath } = await saveScreenshot(stagehand.page, runFolder, 'after', stepCounter);
      screenshotPaths.push(filepath);
    }

    // Give time to see the result
    console.log('\n⏳ Waiting 5 seconds before closing...');
    await new Promise(resolve => setTimeout(resolve, 5000));

  } catch (error) {
    console.error('\n❌ Error during test:', error.message);
    if (error.stack) {
      console.error('\nStack trace:', error.stack);
    }
  } finally {
    // Clean up
    console.log('\n🧹 Cleaning up...');
    await stagehand.close();
    console.log('✅ Browser closed\n');

    // AI Analysis Pipeline (only if screenshots were captured)
    if (captureScreenshots && screenshotPaths.length > 0) {
      console.log('=' .repeat(80));
      console.log('🤖 STARTING AI ANALYSIS PIPELINE');
      console.log('=' .repeat(80) + '\n');

      // Stage 1: Vision Model Analysis
      const visionCritique = await analyzeScreenshotsWithVision(screenshotPaths, openrouterApiKey);
      
      console.log('═'.repeat(80));
      console.log('👁️  VISION MODEL CRITIQUE:');
      console.log('═'.repeat(80));
      console.log(visionCritique);
      console.log('═'.repeat(80) + '\n');

      // Stage 2: Summary Analysis
      const summary = await generateSummary(visionCritique, terminalOutput, openrouterApiKey);
      
      console.log('═'.repeat(80));
      console.log('📋 FINAL SUMMARY:');
      console.log('═'.repeat(80));
      console.log(summary);
      console.log('═'.repeat(80) + '\n');

      // Save terminal output
      await saveTerminalOutput(runFolder, terminalOutput);

      // Final output
      console.log('📁 All files saved to:', runFolder);
    }

    // Restore console
    restoreConsole();
  }
}

// Run the test
runTest();
