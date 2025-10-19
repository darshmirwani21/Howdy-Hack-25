#!/usr/bin/env node
/**
 * Stagehand Browser Automation Runner with Visual UI Testing
 * 
 * CLI tool for AI-powered browser testing with screenshot capture, AI analysis, and optional Electron UI
 * Uses Observe + Act pattern: observe to identify actions, then act to execute them
 * 
 * Usage: node runner.js --url <URL> --test "<test description>" [--screenshots] [--ui]
 */

import { Stagehand } from '@browserbasehq/stagehand';
import dotenv from 'dotenv';
import { parseArgs } from 'node:util';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { WebSocketServer } from 'ws';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from main folder (parent directory)
const mainFolderPath = path.resolve(__dirname, '..');
dotenv.config({ path: path.join(mainFolderPath, '.env') });

// Console output capture
let terminalOutput = [];
const originalConsole = {
  log: console.log,
  error: console.error,
  warn: console.warn,
  info: console.info
};

// WebSocket server and clients
let wss = null;
let wsClients = [];

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

// WebSocket message sender
function sendToUI(message) {
  if (wsClients.length > 0) {
    const payload = JSON.stringify(message);
    wsClients.forEach(client => {
      if (client.readyState === 1) { // OPEN
        client.send(payload);
      }
    });
  }
}

// Start WebSocket server
function startWebSocketServer(port) {
  return new Promise((resolve) => {
    wss = new WebSocketServer({ port });
    
    wss.on('connection', (ws) => {
      console.log('UI client connected');
      wsClients.push(ws);
      
      ws.on('close', () => {
        wsClients = wsClients.filter(client => client !== ws);
        console.log('UI client disconnected');
      });
    });
    
    wss.on('listening', () => {
      console.log(`WebSocket server listening on port ${port}`);
      resolve();
    });
  });
}

// Spawn Electron UI
function spawnElectronUI(port) {
  // Look for electron in root node_modules (parent directory)
  const electronPath = path.join(mainFolderPath, 'node_modules', '.bin', 'electron');
  const mainPath = path.join(__dirname, 'ui', 'main.cjs');
  
  const electron = spawn(electronPath, [mainPath], {
    env: { ...process.env, WS_PORT: port },
    stdio: 'inherit'
  });
  
  electron.on('error', (err) => {
    console.error('Failed to start Electron:', err);
  });
  
  return electron;
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
      screenshots: {
        type: 'boolean',
        short: 's',
        default: false
      },
      ui: {
        type: 'boolean',
        default: false
      },
      agent: {
        type: 'boolean',
        short: 'a',
        default: false
      }
    }
  });

  if (!values.url || !values.test) {
    console.error('Error: Both --url and --test arguments are required\n');
    console.log('Usage: node runner.js --url <URL> --test "<test description>" [--agent] [--screenshots] [--ui]\n');
    console.log('Examples:');
    console.log('  node runner.js --url https://example.com --test "Click the login button"');
    console.log('  node runner.js --url https://example.com --test "Navigate to pricing" --screenshots');
    console.log('  node runner.js --url https://example.com --test "Check UI" --screenshots --ui\n');
    process.exit(1);
  }

  return {
    url: values.url,
    test: values.test,
    captureScreenshots: values.screenshots,
    useUI: values.ui,
    useAgent: values.agent
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
  console.log(`Screenshot saved: ${filename}`);
  
  // Read screenshot as base64 for UI
  const imageBuffer = await fs.readFile(filepath);
  const base64Image = imageBuffer.toString('base64');
  
  return { filepath, filename, base64Image };
}

// Save terminal output to file
async function saveTerminalOutput(runFolder, output) {
  const filepath = path.join(runFolder, 'terminal_output.txt');
  await fs.writeFile(filepath, output.join('\n'), 'utf-8');
  console.log(`Terminal output saved: terminal_output.txt`);
}

// Vision Model Analysis - Single screenshot
async function critiqueScreenshot(screenshotPath, openrouterApiKey) {
  try {
    const imageBuffer = await fs.readFile(screenshotPath);
    const base64Image = imageBuffer.toString('base64');
    
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openrouterApiKey}`,
        'HTTP-Referer': 'https://github.com/browserbase/stagehand',
        'X-Title': 'Stagehand UI Analysis'
      },
      body: JSON.stringify({
        model: 'openai/gpt-5-mini',
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: `Analyze this UI screenshot. Be concise and constructive.

**Format your response as:**

## Pros
- List what's working well (design, UX, accessibility, visual hierarchy)

## Cons  
- List any issues (visual glitches, layout problems, UX issues, accessibility concerns)

**Important:** If the design is good overall, say so! Only critique actual problems. Be specific but brief.`
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
    
    if (data.error) {
      throw new Error(data.error.message || JSON.stringify(data.error));
    }
    
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Failed to get vision model critique:', error.message);
    return 'Vision model analysis failed: ' + error.message;
  }
}

// Vision Model Analysis - All screenshots in one call
async function analyzeScreenshotsWithVision(screenshotPaths, openrouterApiKey) {
  try {
    console.log('\nRunning vision model analysis on all screenshots...');
    
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
        text: `Analyze these UI screenshots from a test workflow. Be concise and constructive.

**Format your response as:**

## Overall Assessment
Brief summary of the UI journey and quality

## Pros
- What's working well across the pages

## Cons
- Any issues or concerns found

**Important:** If the design is good, say so! Focus on actual problems, not nitpicks. Be specific but brief.`
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
        model: 'openai/gpt-5-mini',
        messages: [
          {
            role: 'user',
            content: messageContent
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
    console.error('Failed to get vision model critique:', error.message);
    return 'Vision model analysis failed: ' + error.message;
  }
}

// Summary Analysis with GPT-5-mini
async function generateSummary(visionCritique, terminalOutput, openrouterApiKey) {
  try {
    console.log('Generating summary...\n');
    
    const prompt = `Analyze these browser testing results. Be concise and actionable.

**Format your response as:**

## Test Summary
Brief overview of what was tested

## UI Quality
Your assessment based on the visual analysis

## Pros
- What's working well

## Cons
- Issues found (if any)

## Recommendations
- Key action items (if needed)

**Important:** If everything looks good, say so! Be honest and constructive.

---

VISUAL ANALYSIS:
${visionCritique}

TEST LOG (last 50 lines):
${terminalOutput.slice(-50).join('\n')}`;

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openrouterApiKey}`,
        'HTTP-Referer': 'https://github.com/browserbase/stagehand',
        'X-Title': 'Stagehand Test Summary'
      },
      body: JSON.stringify({
        model: 'openai/gpt-5-mini',
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 600
      })
    });

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error.message || JSON.stringify(data.error));
    }
    
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Failed to generate summary:', error.message);
    return 'Summary generation failed: ' + error.message;
  }
}

async function runTest() {
  const { url, test, captureScreenshots, useUI, useAgent } = parseArguments();

  // Validate environment variables
  const openrouterApiKey = process.env.OPENROUTER_API_KEY;
  const modelName = process.env.STAGEHAND_MODEL || 'openai/gpt-5-mini';

  if (!openrouterApiKey) {
    console.error('Error: OPENROUTER_API_KEY environment variable is required');
    console.error('Please set it in your .env file or environment\n');
    process.exit(1);
  }

  // Force Playwright headless mode if UI is enabled
  if (useUI) {
    process.env.PLAYWRIGHT_HEADLESS = '1';
    process.env.HEADLESS = 'true';
    console.log('Browser will run in headless mode (no window)\n');
  }

  // Start WebSocket server and Electron UI if requested
  let electronProcess = null;
  if (useUI) {
    const wsPort = 9876;
    await startWebSocketServer(wsPort);
    console.log('Starting Electron UI...');
    electronProcess = spawnElectronUI(wsPort);
    // Wait a bit for Electron to start
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  // Start capturing console output
  captureConsoleOutput();

  // Setup run folder if screenshots enabled
  let runFolder = null;
  let screenshotPaths = [];
  let stepCounter = 0;
  let cdpSession = null;
  
  if (captureScreenshots) {
    runFolder = await createRunFolder();
    console.log(`Run folder created: ${runFolder}\n`);
  }

  console.log('Starting Stagehand Browser Automation');
  console.log('=' .repeat(80));
  console.log(`Target URL: ${url}`);
  console.log(`Test: ${test}`);
  console.log(`Model: ${modelName}`);
  console.log(`Mode: ${useAgent ? 'Computer Use Agent (CU)' : 'Normal (single action)'}`);
  console.log(`Screenshots: ${captureScreenshots ? 'Enabled' : 'Disabled'}`);
  console.log(`UI Dashboard: ${useUI ? 'Enabled' : 'Disabled'}`);
  console.log('=' .repeat(80));

  // Send initial status to UI
  sendToUI({ type: 'status', message: 'Initializing...', url: null });

  // Initialize Stagehand with LOCAL environment
  const stagehand = new Stagehand({
    env: 'LOCAL',
    headless: true, // Always run in headless mode
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
    console.log('\nInitializing Stagehand...');
    sendToUI({ type: 'status', message: 'Initializing Stagehand...' });
    await stagehand.init();
    console.log('Stagehand initialized\n');

    // Navigate to URL
    console.log(`Navigating to ${url}...`);
    sendToUI({ type: 'status', message: `Navigating to ${url}...`, url });
    await stagehand.page.goto(url);
    console.log('Page loaded\n');
    sendToUI({ type: 'status', message: 'Page loaded', url });

    // Start CDP screencast for live UI preview
    if (useUI) {
      console.log('Starting CDP screencast for live UI...');
      cdpSession = await stagehand.context.newCDPSession(stagehand.page);
      
      await cdpSession.send('Page.startScreencast', {
        format: 'png',
        maxWidth: 1280,
        maxHeight: 720
      });

      let frameCount = 0;
      cdpSession.on('Page.screencastFrame', async ({ data, sessionId }) => {
        frameCount++;
        if (frameCount === 1) {
          console.log('📺 First CDP frame received, streaming to UI...');
        }
        if (frameCount % 10 === 0) {
          console.log(`📺 Streamed ${frameCount} frames to UI`);
        }
        // Send frame to UI
        sendToUI({ type: 'viewport', image: data, url: stagehand.page.url() });
        // Acknowledge frame to keep stream going
        await cdpSession.send('Page.screencastFrameAck', { sessionId });
      });

      console.log('CDP screencast started\n');
      console.log(`Connected UI clients: ${wsClients.length}`);
      
      // Add error handling for CDP session
      cdpSession.on('disconnected', () => {
        console.log('CDP session disconnected');
      });
    }

    // Setup screenshot capture on URL change
    if (captureScreenshots) {
      let lastUrl = url;
      let screenshotTimer = null;
      
      // Capture screenshot after page settles
      const captureScreenshot = async (urlAtScheduleTime) => {
        stepCounter++;
        console.log(`Page navigated to ${urlAtScheduleTime} - capturing full page screenshot...`);
        sendToUI({ type: 'status', message: 'Capturing screenshot...' });
        
        try {
          const { filepath, filename, base64Image } = await saveScreenshot(stagehand.page, runFolder, 'step', stepCounter);
          screenshotPaths.push(filepath);
          
          // Send to UI
          sendToUI({ 
            type: 'screenshot', 
            image: base64Image, 
            step: stepCounter, 
            prefix: 'step',
            filename 
          });
          
          // Run critique in parallel (non-blocking)
          if (useUI) {
            console.log('Running AI critique in parallel...');
            critiqueScreenshot(filepath, openrouterApiKey).then(critique => {
              sendToUI({ type: 'critique', step: stepCounter, critique });
              console.log(`Critique complete for step ${stepCounter}\n`);
            }).catch(err => {
              console.error(`Critique failed for step ${stepCounter}:`, err.message);
            });
          }
        } catch (error) {
          console.error('Failed to capture screenshot:', error.message);
        }
      };
      
      // Debounced screenshot scheduler
      const scheduleScreenshot = (urlToCapture) => {
        // Clear any pending screenshot
        if (screenshotTimer) {
          clearTimeout(screenshotTimer);
        }
        
        // Schedule screenshot after 0.5s (handles redirects)
        screenshotTimer = setTimeout(async () => {
          const finalUrl = stagehand.page.url();
          // Only capture if URL is still the same (no more redirects)
          if (finalUrl === urlToCapture) {
            await captureScreenshot(finalUrl);
          }
        }, 500);
      };
      
      // Capture initial page
      scheduleScreenshot(url);
      
      // Listen for page navigations
      stagehand.page.on('framenavigated', async (frame) => {
        if (frame === stagehand.page.mainFrame()) {
          const currentUrl = stagehand.page.url();
          if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            scheduleScreenshot(currentUrl);
          }
        }
      });
    }

    // Run the test using observe + act pattern
    sendToUI({ type: 'status', message: 'Running test...' });
    

    if (useAgent) {
      // Computer Use (CU) Agent Mode - Multi-step autonomous
      console.log('Starting Computer Use Agent (multi-step autonomous)...');
      console.log('-'.repeat(80));
      
      const agent = stagehand.agent({
        model: modelName
      });
      
      const result = await agent.execute(test);
      
      console.log('-'.repeat(80));
      console.log('Computer Use Agent completed!\n');
      console.log('Result:', result);
    } else {
      // Normal Mode - Observe + Act pattern
      console.log('🤖 Starting Observe + Act pattern...');
    console.log('-'.repeat(80));
    
    const page = stagehand.page;
    
    // Step 1: Observe - Find elements/actions based on the instruction
    console.log('👁️  Step 1: Observing page to identify actions...');
    const observations = await page.observe(test);
    
    console.log(`✅ Found ${observations.length} possible action(s):\n`);
    observations.forEach((obs, index) => {
      console.log(`   ${index + 1}. ${obs.description || 'Action'}`);
      console.log(`      Method: ${obs.method}`);
      console.log(`      Selector: ${obs.selector}\n`);
    });
    
    // Step 2: Act - Execute each observed action
    if (observations.length > 0) {
      console.log('🎬 Step 2: Executing observed actions...\n');
      
      for (let i = 0; i < observations.length; i++) {
        const observation = observations[i];
        console.log(`   Executing action ${i + 1}/${observations.length}: ${observation.description || 'Action'}`);
        
        try {
          // Perform the action using the observation result
          await page.act({
            action: observation.method,
            selector: observation.selector,
            args: observation.arguments
          });
          
          console.log(`   ✅ Action ${i + 1} completed successfully\n`);
          
          // Wait a bit between actions
          if (i < observations.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        } catch (error) {
          console.error(`   ❌ Action ${i + 1} failed:`, error.message);
        }
      }
    } else {
      console.log('⚠️  No actions found to execute\n');
    }

    console.log('-'.repeat(80));
    console.log('✅ Observe + Act pattern completed!\n');

    // Capture "after" screenshot
    if (captureScreenshots) {
      stepCounter++;
      console.log('📸 Capturing AFTER screenshot...');
      sendToUI({ type: 'status', message: 'Capturing AFTER screenshot...' });
      
      const { filepath, filename, base64Image } = await saveScreenshot(stagehand.page, runFolder, 'after', stepCounter);
      screenshotPaths.push(filepath);
      
      // Send to UI
      sendToUI({ 
        type: 'screenshot', 
        image: base64Image, 
        step: stepCounter, 
        prefix: 'after',
        filename 
      });
      
      // Run critique immediately (real-time)
      if (useUI) {
        console.log('🔍 Running AI critique...');
        const critique = await critiqueScreenshot(filepath, openrouterApiKey);
        sendToUI({ type: 'critique', step: stepCounter, critique });
        console.log(`✅ Critique complete\n`);
      }
    }
    }

    // Give time to see the result
    console.log('\nWaiting 5 seconds before closing...');
    await new Promise(resolve => setTimeout(resolve, 5000));

  } catch (error) {
    console.error('\nError during test:', error.message);
    if (error.stack) {
      console.error('\nStack trace:', error.stack);
    }
    sendToUI({ type: 'status', message: 'Error: ' + error.message });
  } finally {
    // Stop CDP screencast if running
    if (cdpSession) {
      try {
        await cdpSession.send('Page.stopScreencast');
        console.log('CDP screencast stopped');
      } catch (e) {
        // Ignore errors during cleanup
      }
    }

    // Clean up
    console.log('\n🧹 Cleaning up...');
    await stagehand.close();
    console.log('Browser closed\n');

    // AI Analysis Pipeline (only if screenshots were captured)
    if (captureScreenshots && screenshotPaths.length > 0) {
      console.log('=' .repeat(80));
      console.log('STARTING AI ANALYSIS PIPELINE');
      console.log('=' .repeat(80) + '\n');

      // Stage 1: Vision Model Analysis (batch mode for terminal output)
      const visionCritique = await analyzeScreenshotsWithVision(screenshotPaths, openrouterApiKey);
      
      console.log('═'.repeat(80));
      console.log('VISION MODEL CRITIQUE:');
      console.log('═'.repeat(80));
      console.log(visionCritique);
      console.log('═'.repeat(80) + '\n');

      // Stage 2: Summary Analysis
      sendToUI({ type: 'status', message: 'Generating final summary...' });
      const summary = await generateSummary(visionCritique, terminalOutput, openrouterApiKey);
      
      // Print summary to terminal (restored console)
      restoreConsole();
      console.log('\n' + '═'.repeat(80));
      console.log('FINAL SUMMARY:');
      console.log('═'.repeat(80));
      console.log(summary);
      console.log('═'.repeat(80) + '\n');

      // Send summary to UI
      sendToUI({ type: 'summary', summary });

      // Save terminal output
      await saveTerminalOutput(runFolder, terminalOutput);

      // Final output
      console.log('All files saved to:', runFolder);
    } else {
      // Restore console if no screenshots
      restoreConsole();
    }

    // Send completion signal
    sendToUI({ type: 'complete', message: 'Test completed' });

    // Auto-close UI and exit after 2 seconds
    if (useUI && electronProcess) {
      console.log('\nTest complete. Closing UI in 2 seconds...\n');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Send close signal to Electron
      sendToUI({ type: 'close' });
      
      // Wait for graceful close
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Force kill electron if still running
      try {
        electronProcess.kill();
      } catch (e) {
        // Already closed
      }
    }
    
    // Close WebSocket server if it exists
    if (wss) {
      wss.close();
    }
    
    console.log('Exiting...\n');
    process.exit(0);
  }
}

// Run the test
runTest();
