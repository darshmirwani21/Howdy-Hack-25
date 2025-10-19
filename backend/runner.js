#!/usr/bin/env node
/**
 * Stagehand Browser Automation Runner
 * 
 * Simple CLI tool for AI-powered browser testing using Stagehand and OpenRouter
 * 
 * Usage: node runner.js --url <URL> --test "<test description>"
 */

import { Stagehand } from '@browserbasehq/stagehand';
import dotenv from 'dotenv';
import { parseArgs } from 'node:util';

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
      }
    }
  });

  if (!values.url || !values.test) {
    console.error('❌ Error: Both --url and --test arguments are required\n');
    console.log('Usage: node runner.js --url <URL> --test "<test description>" [--agent]\n');
    console.log('Examples:');
    console.log('  node runner.js --url https://example.com --test "Click the login button"');
    console.log('  node runner.js --url https://example.com --test "Navigate to pricing and compare plans" --agent\n');
    process.exit(1);
  }

  return {
    url: values.url,
    test: values.test,
    useAgent: values.agent
  };
}

async function runTest() {
  const { url, test, useAgent } = parseArguments();

  // Validate environment variables
  const openrouterApiKey = process.env.OPENROUTER_API_KEY;
  const modelName = process.env.STAGEHAND_MODEL || 'openai/gpt-4o-mini';

  if (!openrouterApiKey) {
    console.error('❌ Error: OPENROUTER_API_KEY environment variable is required');
    console.error('Please set it in your .env file or environment\n');
    process.exit(1);
  }

  console.log('🚀 Starting Stagehand Browser Automation');
  console.log('=' .repeat(80));
  console.log(`🌐 Target URL: ${url}`);
  console.log(`🧪 Test: ${test}`);
  console.log(`🤖 Model: ${modelName}`);
  console.log(`🎯 Mode: ${useAgent ? 'Computer Use Agent (CU)' : 'Normal (single action)'}`);
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

    // Give time to see the result
    console.log('\n⏳ Waiting 3 seconds before closing...');
    await new Promise(resolve => setTimeout(resolve, 3000));

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

