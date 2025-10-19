# Lumen MCP Server - Setup Guide

Complete guide to setting up and using the Lumen MCP Server with your AI assistant.

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd mcp-server
npm install
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
STAGEHAND_MODEL=openai/gpt-4o-mini
```

**Get your API key**: https://openrouter.ai/

## 🔧 MCP Client Configuration

### Option 1: Claude Desktop

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lumen": {
      "command": "node",
      "args": ["/Users/YOUR_USERNAME/GitHub/Howdy-Hack-25/mcp-server/src/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-your-key-here"
      }
    }
  }
}
```

**Important**: Replace `/Users/YOUR_USERNAME/GitHub/Howdy-Hack-25` with the actual absolute path to your project.

### Option 2: Cursor IDE

**Location**: Create `.cursor/mcp.json` in your workspace root

```json
{
  "mcpServers": {
    "lumen": {
      "command": "node",
      "args": ["./mcp-server/src/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-your-key-here"
      }
    }
  }
}
```

### Option 3: Other MCP Clients

For other MCP-compatible clients, use:

- **Command**: `node`
- **Args**: `["/absolute/path/to/mcp-server/src/index.js"]`
- **Env**: `{"OPENROUTER_API_KEY": "your-key"}`

## ✅ Verify Installation

### Test 1: Check Server Starts

```bash
cd mcp-server
node src/index.js
```

You should see:
```
🚀 Starting Lumen MCP Server...
📋 Available tools: run_browser_test, run_agent_test, analyze_screenshot, get_test_results, list_test_runs
✅ Lumen MCP Server running
```

Press `Ctrl+C` to stop.

### Test 2: Verify in AI Assistant

After configuring your MCP client and restarting it, ask:

```
"What MCP tools do you have available?"
```

You should see Lumen tools listed, including:
- `run_browser_test`
- `run_agent_test`
- `analyze_screenshot`
- `get_test_results`
- `list_test_runs`

## 🎯 Usage Examples

### Example 1: Simple Button Click Test

Ask your AI assistant:

```
"Use Lumen to test clicking the 'Get Started' button on https://example.com"
```

The AI will call:
```javascript
run_browser_test({
  url: "https://example.com",
  test: "click the Get Started button",
  captureScreenshots: true
})
```

### Example 2: Multi-Step Workflow

```
"Run an agent test on https://myapp.com to sign up for a new account with email test@example.com"
```

The AI will call:
```javascript
run_agent_test({
  url: "https://myapp.com",
  test: "sign up for a new account with email test@example.com",
  captureScreenshots: true,
  analyzeUI: true
})
```

### Example 3: UI Analysis

```
"Analyze the UI quality of https://mywebsite.com homepage"
```

The AI will:
1. Run a test to navigate to the page
2. Capture screenshots
3. Analyze with vision AI
4. Provide detailed feedback

### Example 4: Get Previous Results

```
"Show me the results from the last browser test"
```

The AI will call:
```javascript
get_test_results({})
```

## 🔍 Troubleshooting

### Issue: "OPENROUTER_API_KEY environment variable is not set"

**Solution**: Make sure you've set the API key in your MCP client config:

```json
"env": {
  "OPENROUTER_API_KEY": "sk-or-v1-your-actual-key"
}
```

### Issue: "Tool not found" or tools not showing up

**Solution**: 
1. Check that the path in your MCP config is absolute and correct
2. Restart your MCP client completely
3. Check the client's logs for errors

### Issue: Browser tests fail to start

**Solution**:
1. Make sure you have Chrome/Chromium installed
2. Check that Playwright can access the browser: `npx playwright install chromium`
3. Run from the mcp-server directory: `cd mcp-server && npm install`

### Issue: Screenshots not captured

**Solution**:
1. Make sure `captureScreenshots: true` is set
2. Check that the `screenshots/` directory is writable
3. Screenshots are saved in `mcp-server/screenshots/run_*/`

## 📊 Understanding Test Results

### Test Run Structure

```json
{
  "runId": "run_1_1234567890",
  "url": "https://example.com",
  "test": "click the login button",
  "mode": "observe_act",
  "success": true,
  "screenshots": [...],
  "testResults": {
    "observations": [...],
    "actions": [...]
  },
  "analysis": {
    "visionCritique": "...",
    "summary": "..."
  }
}
```

### Screenshot Access

Screenshots are accessible via MCP resources:

```
screenshot://run_1_1234567890/1
screenshot://run_1_1234567890/2
```

## 🚀 Advanced Usage

### Custom Model Selection

Set in `.env`:

```bash
STAGEHAND_MODEL=anthropic/claude-3-5-sonnet
```

Available models:
- `openai/gpt-4o-mini` (default, free)
- `openai/gpt-4o`
- `anthropic/claude-3-5-sonnet`
- `google/gemini-pro`
- See more at: https://openrouter.ai/models

### Programmatic Access

You can also use the MCP server programmatically:

```javascript
import { BrowserTestManager } from './src/browser-manager.js';

const manager = new BrowserTestManager();
const result = await manager.runTest(
  'https://example.com',
  'click the login button',
  { captureScreenshots: true, openrouterApiKey: 'your-key' }
);
```

## 📝 Best Practices

1. **Be Specific**: Describe tests clearly ("click the blue 'Sign Up' button in the header")
2. **Use Agent Mode for Workflows**: Multi-step processes work better with `run_agent_test`
3. **Enable Screenshots**: Always useful for debugging and analysis
4. **Check Results**: Use `get_test_results` to review what happened
5. **Start Simple**: Test basic interactions before complex workflows

## 🆘 Getting Help

- Check the main README.md for architecture details
- Review the tool definitions in `src/tools.js`
- Enable verbose logging by running the server directly
- Check MCP client logs for connection issues

## 🎉 You're Ready!

Your Lumen MCP Server is now configured and ready to use. Ask your AI assistant to run browser tests, and it will use the MCP server automatically!
