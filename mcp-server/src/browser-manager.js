/**
 * Browser Manager for Lumen MCP Server
 * Manages Stagehand instances, test execution, and AI analysis
 */

import { Stagehand } from '@browserbasehq/stagehand';
import fs from 'fs/promises';
import { ScreenshotHandler } from './screenshot-handler.js';
import { executeObserveAct, executeAgent } from './test-executor.js';

export class BrowserTestManager {
  constructor() {
    this.stagehand = null;
    this.currentRun = null;
    this.testResults = new Map();
    this.runCounter = 0;
  }

  /**
   * Initialize Stagehand with configuration
   */
  async initialize(config = {}) {
    const {
      openrouterApiKey,
      modelName = 'openai/gpt-5-mini',
      headless = true,
      verbose = 1
    } = config;

    if (!openrouterApiKey) {
      throw new Error('OpenRouter API key is required');
    }

    console.log('Initializing Stagehand...');
    
    this.stagehand = new Stagehand({
      env: 'LOCAL',
      headless,
      verbose,
      debugDom: true,
      enableCaching: false,
      modelName,
      modelClientOptions: {
        apiKey: openrouterApiKey,
        baseURL: 'https://openrouter.ai/api/v1',
        defaultHeaders: {
          'HTTP-Referer': 'https://github.com/browserbase/stagehand',
          'X-Title': 'Lumen MCP Browser Testing'
        }
      }
    });

    await this.stagehand.init();
    console.log('✅ Stagehand initialized');
    
    return true;
  }

  /**
   * Execute a browser test
   */
  async runTest(url, test, options = {}) {
    const {
      captureScreenshots = false,
      useAgent = false,
      modelName = 'openai/gpt-5-mini',
      openrouterApiKey
    } = options;

    if (!this.stagehand) {
      await this.initialize({ openrouterApiKey, modelName });
    }

    this.runCounter++;
    const runId = `run_${this.runCounter}_${Date.now()}`;
    
    const testRun = {
      runId,
      url,
      test,
      mode: useAgent ? 'agent' : 'observe_act',
      startTime: new Date().toISOString(),
      endTime: null,
      screenshots: [],
      testResults: null,
      analysis: null,
      success: false,
      error: null
    };

    this.currentRun = testRun;

    try {
      // Setup screenshot handler if needed
      let screenshotHandler = null;
      if (captureScreenshots) {
        const runFolder = await ScreenshotHandler.createRunFolder();
        screenshotHandler = new ScreenshotHandler(runFolder);
        testRun.runFolder = runFolder;
        console.log(`📁 Run folder created: ${runFolder}`);
      }

      // Navigate to URL
      console.log(`🌐 Navigating to ${url}...`);
      await this.stagehand.page.goto(url);
      console.log('✅ Page loaded');

      // Setup auto-capture if screenshots enabled
      if (screenshotHandler) {
        await screenshotHandler.setupAutoCapture(this.stagehand.page, url);
      }

      // Execute the test
      console.log(`🧪 Running test: "${test}"`);
      let testResults;
      
      if (useAgent) {
        testResults = await executeAgent(this.stagehand, test, modelName);
      } else {
        testResults = await executeObserveAct(this.stagehand.page, test);
      }

      testRun.testResults = testResults;
      testRun.success = testResults.success;

      // Capture final screenshot if enabled
      if (screenshotHandler) {
        console.log('📸 Capturing final screenshot...');
        const finalScreenshot = await screenshotHandler.captureScreenshot(
          this.stagehand.page, 
          'final'
        );
        testRun.screenshots = screenshotHandler.getScreenshots();
        
        // Run AI analysis if API key provided
        if (openrouterApiKey && testRun.screenshots.length > 0) {
          console.log('🤖 Running AI analysis...');
          const analysis = await this.analyzeTestRun(testRun, openrouterApiKey);
          testRun.analysis = analysis;
        }
        
        screenshotHandler.cleanup();
      }

      testRun.endTime = new Date().toISOString();
      this.testResults.set(runId, testRun);

      console.log(`✅ Test completed: ${testRun.success ? 'SUCCESS' : 'FAILED'}`);
      
      return testRun;

    } catch (error) {
      testRun.success = false;
      testRun.error = error.message;
      testRun.endTime = new Date().toISOString();
      this.testResults.set(runId, testRun);
      
      console.error('❌ Test failed:', error.message);
      throw error;
    }
  }

  /**
   * Analyze a single screenshot with vision model
   */
  async critiqueScreenshot(screenshotPath, openrouterApiKey) {
    try {
      const imageBuffer = await fs.readFile(screenshotPath);
      const base64Image = imageBuffer.toString('base64');
      
      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${openrouterApiKey}`,
          'HTTP-Referer': 'https://github.com/browserbase/stagehand',
          'X-Title': 'Lumen UI Analysis'
        },
        body: JSON.stringify({
          model: 'openai/gpt-4o-mini',
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

  /**
   * Analyze all screenshots in a test run
   */
  async analyzeScreenshotsWithVision(screenshotPaths, openrouterApiKey) {
    try {
      console.log('🔍 Running vision model analysis on all screenshots...');
      
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
          'X-Title': 'Lumen UI Analysis'
        },
        body: JSON.stringify({
          model: 'openai/gpt-4o-mini',
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

  /**
   * Generate summary analysis
   */
  async generateSummary(visionCritique, testResults, openrouterApiKey) {
    try {
      console.log('📝 Generating summary...');
      
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

TEST RESULTS:
${JSON.stringify(testResults, null, 2)}`;

      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${openrouterApiKey}`,
          'HTTP-Referer': 'https://github.com/browserbase/stagehand',
          'X-Title': 'Lumen Test Summary'
        },
        body: JSON.stringify({
          model: 'openai/gpt-4o-mini',
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

  /**
   * Analyze a complete test run
   */
  async analyzeTestRun(testRun, openrouterApiKey) {
    const analysis = {
      visionCritique: null,
      summary: null
    };

    try {
      if (testRun.screenshots && testRun.screenshots.length > 0) {
        const screenshotPaths = testRun.screenshots.map(s => s.filepath);
        
        // Get vision analysis
        analysis.visionCritique = await this.analyzeScreenshotsWithVision(
          screenshotPaths, 
          openrouterApiKey
        );
        
        // Generate summary
        analysis.summary = await this.generateSummary(
          analysis.visionCritique,
          testRun.testResults,
          openrouterApiKey
        );
      }
    } catch (error) {
      console.error('Analysis failed:', error.message);
    }

    return analysis;
  }

  /**
   * Get test results by run ID
   */
  getTestResults(runId) {
    return this.testResults.get(runId) || null;
  }

  /**
   * Get all test results
   */
  getAllTestResults() {
    return Array.from(this.testResults.values());
  }

  /**
   * Get the current/last test run
   */
  getCurrentRun() {
    return this.currentRun;
  }

  /**
   * Cleanup and close browser
   */
  async cleanup() {
    if (this.stagehand) {
      console.log('🧹 Cleaning up browser...');
      await this.stagehand.close();
      this.stagehand = null;
      console.log('✅ Browser closed');
    }
  }
}
