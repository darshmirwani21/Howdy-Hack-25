#!/usr/bin/env node
/**
 * Stagehand Browser Automation Runner with Visual UI Testing
 * 
 * CLI tool for AI-powered browser testing with screenshot capture and AI critique
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
      },
      critique: {
        type: 'boolean',
        short: 'c',
        default: false
      }
    }
  });

  if (!values.url || !values.test) {
    console.error('❌ Error: Both --url and --test arguments are required\n');
    console.log('Usage: node runner.js --url <URL> --test "<test description>" [--agent] [--screenshots] [--critique]\n');
    console.log('Examples:');
    console.log('  node runner.js --url https://example.com --test "Click the login button"');
    console.log('  node runner.js --url https://example.com --test "Navigate to pricing" --agent --screenshots');
    console.log('  node runner.js --url https://example.com --test "Check homepage UI" --screenshots --critique\n');
    process.exit(1);
  }

  return {
    url: values.url,
    test: values.test,
    useAgent: values.agent,
    captureScreenshots: values.screenshots,
    aiCritique: values.critique
  };
}

// Create screenshots directory
async function ensureScreenshotsDir() {
  const screenshotsDir = path.join(__dirname, 'screenshots');
  try {
    await fs.access(screenshotsDir);
  } catch {
    await fs.mkdir(screenshotsDir, { recursive: true });
  }
  return screenshotsDir;
}

// Save screenshot with timestamp
async function saveScreenshot(page, screenshotsDir, prefix, stepNumber) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${prefix}_step${stepNumber}_${timestamp}.png`;
  const filepath = path.join(screenshotsDir, filename);
  
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`📸 Screenshot saved: ${filename}`);
  return filepath;
}

// AI Critique using OpenRouter Vision Model
async function critiqueScreenshot(screenshotPath, context, openrouterApiKey) {
  try {
    const imageBuffer = await fs.readFile(screenshotPath);
    const base64Image = imageBuffer.toString('base64');
    
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openrouterApiKey}`,
        'HTTP-Referer': 'https://github.com/browserbase/stagehand',
        'X-Title': 'Stagehand UI Critique'
      },
      body: JSON.stringify({
        model: 'openai/gpt-4o', // Vision-capable model
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: `You are a UI/UX expert reviewing this screenshot. Context: ${context}

Analyze the screenshot and provide:
1. UI/UX issues (broken layouts, overlapping elements, poor contrast, etc.)
2. Accessibility concerns
3. Visual bugs or glitches
4. Overall quality assessment (1-10)
5. Specific actionable feedback

Be concise but thorough.`
              },
              {
                type: 'image_url',
                image_url: {
                  url: `data:image/png;base64,${base64Image}`
                }
              }
            ]
          }
        ],
        max_tokens: 500
      })
    });

    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('⚠️  Failed to get AI critique:', error.message);
    return null;
  }
}

async function runTest() {
  const { url, test, useAgent, captureScreenshots, aiCritique } = parseArguments();

  // Validate environment variables
  const openrouterApiKey = process.env.OPENROUTER_API_KEY;
  const modelName = process.env.STAGEHAND_MODEL || 'openai/gpt-4o-mini';

  if (!openrouterApiKey) {
    console.error('❌ Error: OPENROUTER_API_KEY environment variable is required');
    console.error('Please set it in your .env file or environment\n');
    process.exit(1);
  }

  // Setup screenshots directory if needed
  let screenshotsDir = null;
  let stepCounter = 0;
  if (captureScreenshots) {
    screenshotsDir = await ensureScreenshotsDir();
    console.log(`📁 Screenshots will be saved to: ${screenshotsDir}\n`);
  }

  console.log('🚀 Starting Stagehand Browser Automation');
  console.log('=' .repeat(80));
  console.log(`🌐 Target URL: ${url}`);
  console.log(`🧪 Test: ${test}`);
  console.log(`🤖 Model: ${modelName}`);
  console.log(`🎯 Mode: ${useAgent ? 'Computer Use Agent (CU)' : 'Normal (single action)'}`);
  console.log(`📸 Screenshots: ${captureScreenshots ? 'Enabled' : 'Disabled'}`);
  console.log(`🔍 AI Critique: ${aiCritique ? 'Enabled' : 'Disabled'}`);
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
      console.log('\n📸 Capturing BEFORE screenshot...');
      const beforePath = await saveScreenshot(stagehand.page, screenshotsDir, 'before', stepCounter);
      
      if (aiCritique) {
        console.log('🔍 Running AI critique on initial page...\n');
        const critique = await critiqueScreenshot(beforePath, `Initial page load: ${url}`, openrouterApiKey);
        if (critique) {
          console.log('═'.repeat(80));
          console.log('🎨 UI CRITIQUE (Before Action):');
          console.log(critique);
          console.log('═'.repeat(80) + '\n');
        }
      }
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
      const afterPath = await saveScreenshot(stagehand.page, screenshotsDir, 'after', stepCounter);
      
      if (aiCritique) {
        console.log('🔍 Running AI critique on final state...\n');
        const critique = await critiqueScreenshot(afterPath, `After action: ${test}`, openrouterApiKey);
        if (critique) {
          console.log('═'.repeat(80));
          console.log('🎨 UI CRITIQUE (After Action):');
          console.log(critique);
          console.log('═'.repeat(80) + '\n');
        }
      }
    }

    // Give time to see the result
    console.log('\n⏳ Waiting 5 seconds before closing...');
    await new Promise(resolve => setTimeout(resolve, 5000));

  } catch (error) {
    console.error('\n❌ Error during test:', error.message);
    if (error.stack) {
      console.error('\nStack trace:', error.stack);
    }
    process.exit(1);
  } finally {
    // Clean up
    console.log('\n🧹 Cleaning up...');
    await stagehand.close();
    console.log('✅ Done!');
  }
}

// Run the test
runTest();

