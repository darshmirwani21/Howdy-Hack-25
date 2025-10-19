#!/usr/bin/env node

import { Stagehand } from "@browserbasehq/stagehand";
import dotenv from "dotenv";
import { Command } from "commander";
import fs from "fs";
import path from "path";

// Load environment variables from .env file
dotenv.config();

const program = new Command();

program
  .name("stagehand-cli")
  .description("CLI tool to automate browser actions using Stagehand with OpenAI")
  .version("1.0.0")
  .option("-u, --url <url>", "URL to navigate to")
  .option("-a, --action <action>", "Single action to perform")
  .option("-p, --prompt <prompt>", "Multi-action prompt (period-separated)")
  .option("-v, --verbose", "Enable verbose logging")
  .option("--ui", "Launch with Electron UI")
  .allowExcessArguments(false);

// Only parse and validate if running as CLI (not imported by Electron)
let options = {};
const isElectron = process.argv[0].includes('electron');

if (!isElectron) {
  try {
    program.parse(process.argv);
  } catch (error) {
    console.error("Error parsing arguments:", error.message);
    program.help();
    process.exit(1);
  }

  options = program.opts();

  // Validate required options for CLI mode
  if (!options.url) {
    console.error("\n❌ Error: --url is required!\n");
    program.help();
    process.exit(1);
  }

  if (!options.action && !options.prompt) {
    console.error("\n❌ Error: Either --action or --prompt must be provided!\n");
    program.help();
    process.exit(1);
  }
}

// Ensure screenshots directory exists
const screenshotsDir = './screenshots';
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

// Parse prompt into individual actions
function parsePromptToActions(prompt) {
  return prompt
    .split('.')
    .map(s => s.trim())
    .filter(s => s.length > 0);
}

// Execute multiple actions with observation and screenshots
async function executeActionsWithFeedback(stagehand, actions, emitUpdate = null) {
  const results = [];
  
  for (let i = 0; i < actions.length; i++) {
    const action = actions[i];
    const actionResult = {
      index: i,
      action: action,
      timestamp: new Date().toISOString(),
    };
    
    // Emit to UI if available
    if (emitUpdate) {
      emitUpdate('action-start', { index: i, action, total: actions.length });
    }
    
    try {
      console.log(`\n[${i+1}/${actions.length}] Executing: ${action}`);
      
      // Execute action using stagehand.act() per Stagehand docs
      const actResult = await stagehand.page.act(action);
      actionResult.actResult = actResult;
      actionResult.success = true;
      
      // Observe page state after action
      console.log(`  → Observing page state...`);
      const observation = await stagehand.page.observe();
      actionResult.observation = observation;
      
      // Capture screenshot
      const screenshotPath = `./screenshots/action_${i}_${Date.now()}.png`;
      await stagehand.page.screenshot({ path: screenshotPath, fullPage: false });
      actionResult.screenshot = screenshotPath;
      
      console.log(`  ✓ Success`);
      
      if (emitUpdate) {
        emitUpdate('action-complete', actionResult);
      }
      
    } catch (error) {
      actionResult.success = false;
      actionResult.error = error.message;
      console.error(`  ✗ Failed: ${error.message}`);
      
      if (emitUpdate) {
        emitUpdate('action-error', actionResult);
      }
    }
    
    results.push(actionResult);
  }
  
  return results;
}

// Format results for output
function formatResults(results, url) {
  const summary = {
    url: url,
    totalActions: results.length,
    successful: results.filter(r => r.success).length,
    failed: results.filter(r => !r.success).length,
    timestamp: new Date().toISOString(),
    actions: results
  };
  
  const textSummary = generateTextSummary(summary);
  
  return { json: summary, text: textSummary };
}

function generateTextSummary(summary) {
  let text = `## Test Results for ${summary.url}\n\n`;
  text += `Executed ${summary.totalActions} actions: ${summary.successful} succeeded, ${summary.failed} failed\n\n`;
  
  summary.actions.forEach((action, i) => {
    text += `### Action ${i+1}: ${action.action}\n`;
    text += `Status: ${action.success ? '✓ Success' : '✗ Failed'}\n`;
    
    if (action.observation) {
      const obsStr = JSON.stringify(action.observation);
      text += `Page State: ${obsStr.substring(0, 200)}${obsStr.length > 200 ? '...' : ''}\n`;
    }
    
    if (action.error) {
      text += `Error: ${action.error}\n`;
    }
    
    if (action.screenshot) {
      text += `Screenshot: ${action.screenshot}\n`;
    }
    
    text += `\n`;
  });
  
  return text;
}

async function main(emitUpdate = null, customOptions = null) {
  // Use custom options if provided (for Electron), otherwise use CLI options
  const opts = customOptions || options;
  
  console.log(`Initializing Stagehand with OpenAI (gpt-4o)...`);
  
  const openaiApiKey = process.env.OPENAI_API_KEY;
  
  if (!openaiApiKey) {
    console.error("❌ Error: OPENAI_API_KEY environment variable is required!");
    console.error("Add it to your .env file: OPENAI_API_KEY=sk-your-key-here");
    throw new Error("OPENAI_API_KEY not found");
  }
  
  const modelConfig = {
    env: "LOCAL",
    modelName: "gpt-4o",
    modelClientOptions: {
      apiKey: openaiApiKey,
      baseURL: "https://api.openai.com/v1"
    },
    verbose: opts.verbose ? 1 : 0,
    headless: opts.ui ? true : false, // Headless if UI mode
  };
  
  const stagehand = new Stagehand(modelConfig);

  try {
    await stagehand.init();
    console.log("✓ Stagehand initialized successfully!");
    console.log(`   Model: gpt-4o`);
    console.log(`   API: OpenAI`);
    
    if (emitUpdate) {
      emitUpdate('init-complete', { model: 'gpt-4o', provider: 'openai' });
    }
    
    // Navigate to URL
    const targetUrl = opts.url;
    console.log(`\nNavigating to: ${targetUrl}`);
    await stagehand.page.goto(targetUrl);
    console.log("✓ Navigation complete!");
    
    if (emitUpdate) {
      emitUpdate('navigation-complete', { url: targetUrl });
    }
    
    // Determine actions to execute
    let actions = [];
    if (opts.prompt) {
      // Multi-action mode
      actions = parsePromptToActions(opts.prompt);
      console.log(`\nParsed ${actions.length} actions from prompt`);
    } else if (opts.action) {
      // Single action mode (backward compatible)
      actions = [opts.action];
    } else {
      throw new Error("Either --action or --prompt must be provided");
    }
    
    // Execute actions with feedback
    const results = await executeActionsWithFeedback(stagehand, actions, emitUpdate);
    
    // Format and output results
    const formatted = formatResults(results, targetUrl);
    
    // Write JSON file
    const outputFile = `./test-results-${Date.now()}.json`;
    fs.writeFileSync(outputFile, JSON.stringify(formatted.json, null, 2));
    
    // Print text summary
    console.log('\n' + '='.repeat(60));
    console.log('TEST RESULTS');
    console.log('='.repeat(60));
    console.log(formatted.text);
    console.log(`\nFull results saved to: ${outputFile}`);
    
    if (emitUpdate) {
      emitUpdate('test-complete', formatted.json);
    }
    
    return formatted.json;
    
  } catch (error) {
    console.error("\n✗ Error:", error.message);
    if (emitUpdate) {
      emitUpdate('error', { message: error.message, stack: error.stack });
    }
    throw error;
  } finally {
    await stagehand.close();
    console.log("\n✓ Browser closed. Done!");
  }
}

// Export for Electron use
export { main, parsePromptToActions };

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
