/**
 * Screenshot Handler for Lumen MCP Server
 * Manages screenshot capture, storage, and auto-capture on navigation
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class ScreenshotHandler {
  constructor(runFolder) {
    this.runFolder = runFolder;
    this.screenshots = [];
    this.stepCounter = 0;
    this.screenshotTimer = null;
    this.lastUrl = null;
  }

  /**
   * Create a timestamped run folder for screenshots
   */
  static async createRunFolder(baseDir = null) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').split('.')[0];
    const screenshotsDir = baseDir || path.join(__dirname, '..', 'screenshots');
    const runFolder = path.join(screenshotsDir, `run_${timestamp}`);
    await fs.mkdir(runFolder, { recursive: true });
    return runFolder;
  }

  /**
   * Capture a screenshot and save it
   */
  async captureScreenshot(page, prefix = 'step') {
    this.stepCounter++;
    const filename = `${prefix}_step${this.stepCounter}.png`;
    const filepath = path.join(this.runFolder, filename);
    
    await page.screenshot({ path: filepath, fullPage: true });
    
    // Read screenshot as base64
    const imageBuffer = await fs.readFile(filepath);
    const base64Image = imageBuffer.toString('base64');
    
    const screenshotData = {
      filepath,
      filename,
      base64Image,
      step: this.stepCounter,
      prefix,
      timestamp: new Date().toISOString(),
      url: page.url()
    };
    
    this.screenshots.push(screenshotData);
    
    return screenshotData;
  }

  /**
   * Setup automatic screenshot capture on page navigation
   */
  async setupAutoCapture(page, initialUrl) {
    this.lastUrl = initialUrl;
    
    // Debounced screenshot scheduler
    const scheduleScreenshot = (urlToCapture) => {
      // Clear any pending screenshot
      if (this.screenshotTimer) {
        clearTimeout(this.screenshotTimer);
      }
      
      // Schedule screenshot after 500ms (handles redirects)
      this.screenshotTimer = setTimeout(async () => {
        const finalUrl = page.url();
        // Only capture if URL is still the same (no more redirects)
        if (finalUrl === urlToCapture) {
          await this.captureScreenshot(page, 'auto');
        }
      }, 500);
    };
    
    // Capture initial page
    scheduleScreenshot(initialUrl);
    
    // Listen for page navigations
    page.on('framenavigated', async (frame) => {
      if (frame === page.mainFrame()) {
        const currentUrl = page.url();
        if (currentUrl !== this.lastUrl) {
          this.lastUrl = currentUrl;
          scheduleScreenshot(currentUrl);
        }
      }
    });
  }

  /**
   * Get all captured screenshots
   */
  getScreenshots() {
    return this.screenshots;
  }

  /**
   * Get screenshot paths only
   */
  getScreenshotPaths() {
    return this.screenshots.map(s => s.filepath);
  }

  /**
   * Get the latest screenshot
   */
  getLatestScreenshot() {
    return this.screenshots[this.screenshots.length - 1] || null;
  }

  /**
   * Save terminal output to file
   */
  static async saveTerminalOutput(runFolder, output) {
    const filepath = path.join(runFolder, 'terminal_output.txt');
    const content = Array.isArray(output) ? output.join('\n') : output;
    await fs.writeFile(filepath, content, 'utf-8');
    return filepath;
  }

  /**
   * Cleanup timers
   */
  cleanup() {
    if (this.screenshotTimer) {
      clearTimeout(this.screenshotTimer);
      this.screenshotTimer = null;
    }
  }
}
