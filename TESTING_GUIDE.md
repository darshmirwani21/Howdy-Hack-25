# Stagehand Testing Tool - Complete Guide

## Overview

This tool enables Cursor AI (and other IDEs) to automatically test web applications using Stagehand browser automation with Groq LLM. It provides both CLI and visual UI modes for comprehensive testing with real-time feedback.

## Features

- **Multi-Action Testing**: Parse natural language prompts into multiple sequential actions
- **Automatic Observation**: Captures page state after each action using `stagehand.observe()`
- **Screenshot Capture**: Takes screenshots after every action for visual verification
- **Comprehensive Results**: Outputs both JSON and human-readable text summaries
- **Electron UI**: Beautiful dashboard showing live action feed, screenshots, and results
- **Cursor Integration**: Designed to be called automatically by Cursor AI after code changes

## Installation

```bash
# Install dependencies
npm install

# Ensure you have a Groq API key in .env
echo "GROQ_API_KEY=gsk-your-key-here" > .env
```

## Usage

### CLI Mode

#### Single Action (Backward Compatible)
```bash
node index.js --url "http://localhost:3000" --action "click the submit button"
```

#### Multi-Action Prompt (Recommended)
```bash
node index.js --url "http://localhost:3000" --prompt "Navigate to login. Fill username with test. Fill password with pass123. Click submit"
```

#### Verbose Mode
```bash
node index.js --url "http://localhost:3000" --prompt "Test checkout flow" --verbose
```

### UI Mode (Electron Dashboard)

```bash
npm run ui
```

Then:
1. Enter the URL of your web app (e.g., `http://localhost:3000`)
2. Enter your test prompt (e.g., `Navigate to login. Fill form. Click submit`)
3. Click "Run Test"
4. Watch real-time action feed, screenshots, and results

## How It Works

### 1. Prompt Parsing
The tool splits your prompt by periods (`.`) into individual actions:
```
"Navigate to login. Fill username. Click submit"
↓
["Navigate to login", "Fill username", "Click submit"]
```

### 2. Action Execution
For each action:
- Executes using `stagehand.act(action)`
- Observes page state using `stagehand.observe()`
- Captures screenshot using `stagehand.page.screenshot()`
- Stores all results in memory

### 3. Result Compilation
After all actions complete:
- Formats results as JSON and text
- Saves JSON file: `test-results-{timestamp}.json`
- Prints text summary to stdout
- Sends updates to Electron UI (if running)

## Output Formats

### JSON Output
```json
{
  "url": "http://localhost:3000",
  "totalActions": 3,
  "successful": 2,
  "failed": 1,
  "timestamp": "2025-01-19T12:00:00Z",
  "actions": [
    {
      "index": 0,
      "action": "Navigate to login",
      "success": true,
      "observation": { /* page state */ },
      "screenshot": "./screenshots/action_0_1234567890.png",
      "timestamp": "2025-01-19T12:00:01Z"
    }
  ]
}
```

### Text Output
```
## Test Results for http://localhost:3000

Executed 3 actions: 2 succeeded, 1 failed

### Action 1: Navigate to login
Status: ✓ Success
Page State: {"elements":[...]...}
Screenshot: ./screenshots/action_0_1234567890.png

### Action 2: Fill username
Status: ✗ Failed
Error: Element not found
```

## Cursor AI Integration

Add to your workflow:

```bash
# After making UI changes
node index.js --url "http://localhost:3000" --prompt "Test the new feature"
```

Cursor will:
1. Read the text summary from stdout
2. Analyze failures and page states
3. Suggest code fixes based on observations
4. Verify fixes by running tests again

## Best Practices

### Writing Good Prompts

✅ **Good:**
- "Navigate to login page. Fill username field with test@example.com. Click the login button"
- "Scroll to bottom. Click the 'Load More' button. Wait for items to appear"
- "Fill search box with 'laptop'. Press enter. Verify results appear"

❌ **Avoid:**
- "Test the login" (too vague)
- "Click the first button" (ambiguous)
- "Do something with the form" (unclear goal)

### Action Guidelines

1. **Be Specific**: Reference visible text, labels, or clear identifiers
2. **One Goal Per Action**: Each sentence should have a single, clear objective
3. **Use Visible Text**: Reference text that appears on the page
4. **Sequential Steps**: Actions execute in order, so plan accordingly

## Troubleshooting

### "GROQ_API_KEY not found"
- Create a `.env` file with your Groq API key
- Get a key from https://console.groq.com/keys

### "Element not found" errors
- Make your action more specific (e.g., "Click the blue submit button")
- Check if the element is visible on the page
- Review the screenshot to see what's actually on the page

### Electron UI not showing screenshots
- Check that screenshots are being saved to `./screenshots/`
- Verify file permissions
- Look for errors in the Electron DevTools console

### Tests running slowly
- Groq's llama-3.3-70b-versatile is optimized for speed
- Reduce `waitBetweenActions` in the code if needed
- Use simpler, more direct actions

## Advanced Usage

### Custom Wait Times
Edit `index.js` line 83:
```javascript
const actResult = await stagehand.act(action);
// Add custom wait after action
await new Promise(resolve => setTimeout(resolve, 1000));
```

### Different LLM Models
Edit `index.js` line 173:
```javascript
modelName: "groq/llama-3.3-70b-versatile", // Change model here
```

See [Stagehand docs](https://docs.stagehand.dev/configuration/models) for supported models.

### Headless Mode
For CI/CD or automated testing:
```javascript
headless: true, // Line 178 in index.js
```

## File Structure

```
.
├── index.js                    # Main CLI tool
├── electron/
│   ├── main.js                 # Electron main process
│   ├── preload.js              # IPC bridge
│   └── renderer/
│       ├── index.html          # UI layout
│       ├── styles.css          # UI styling
│       └── app.js              # UI logic
├── screenshots/                # Auto-generated screenshots
├── test-results-*.json         # Test result files
└── .env                        # API keys (gitignored)
```

## Contributing

To add new features:
1. Modify `index.js` for CLI functionality
2. Update `electron/renderer/app.js` for UI features
3. Test both CLI and UI modes
4. Update this guide

## License

ISC

