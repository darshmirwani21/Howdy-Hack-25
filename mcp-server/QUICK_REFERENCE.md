# Lumen MCP Server - Quick Reference

## 🛠️ Available Tools

### 1. `run_browser_test`
**Purpose**: Execute a single browser test action  
**Mode**: Observe + Act pattern  
**Best For**: Simple interactions, single actions

**Parameters**:
- `url` (required): Target website URL
- `test` (required): Natural language test description
- `captureScreenshots` (optional): Capture screenshots (default: false)
- `analyzeUI` (optional): Run AI visual analysis (default: false)

**Example Prompts**:
- "Test clicking the login button on https://example.com"
- "Fill out the contact form on https://mysite.com"
- "Navigate to the pricing page on https://app.com"

---

### 2. `run_agent_test`
**Purpose**: Multi-step autonomous browser testing  
**Mode**: Computer Use Agent  
**Best For**: Complex workflows, multi-page journeys

**Parameters**:
- `url` (required): Starting URL
- `test` (required): High-level workflow description
- `captureScreenshots` (optional): Capture screenshots (default: true)
- `analyzeUI` (optional): Run AI visual analysis (default: false)

**Example Prompts**:
- "Run an agent test to sign up for an account on https://app.com"
- "Test the complete checkout process on https://store.com"
- "Navigate through the onboarding flow on https://product.com"

---

### 3. `analyze_screenshot`
**Purpose**: Analyze UI screenshot with vision AI  
**Best For**: Design critique, UX feedback, accessibility review

**Parameters**:
- `screenshotPath` (required): Absolute path to screenshot file

**Example Prompts**:
- "Analyze the screenshot at /path/to/screenshot.png"
- "Give me UX feedback on this screenshot: /path/to/image.png"

---

### 4. `get_test_results`
**Purpose**: Retrieve results from previous test runs  
**Best For**: Reviewing past tests, debugging

**Parameters**:
- `runId` (optional): Specific run ID (if omitted, returns latest)

**Example Prompts**:
- "Show me the results from the last browser test"
- "Get test results for run_1_1234567890"
- "What happened in the previous test?"

---

### 5. `list_test_runs`
**Purpose**: List all executed test runs  
**Best For**: Viewing test history

**Parameters**: None

**Example Prompts**:
- "List all browser tests that have been run"
- "Show me the test history"
- "What tests have been executed?"

---

## 📊 Resources

### Test Run Data
**URI**: `test-run://{runId}`  
**Returns**: Complete test run data (JSON)

### Screenshots
**URI**: `screenshot://{runId}/{step}`  
**Returns**: Individual screenshot (PNG)

### Test List
**URI**: `test-runs://list`  
**Returns**: All test runs summary (JSON)

---

## 🎯 Common Use Cases

### Testing a Button Click
```
"Use Lumen to test clicking the 'Sign Up' button on https://example.com 
with screenshots enabled"
```

### Testing Form Submission
```
"Run a browser test on https://contact.com to fill out the contact form 
with name 'John Doe' and email 'john@example.com'"
```

### Multi-Step Signup Flow
```
"Run an agent test on https://app.com to complete the signup process: 
enter email, verify, and set up profile"
```

### UI Quality Check
```
"Test https://mywebsite.com homepage and analyze the UI quality with 
screenshots and AI analysis"
```

### Checking Previous Results
```
"Show me the results from the last test including screenshots and analysis"
```

---

## ⚡ Quick Tips

1. **Always include the full URL** with `https://`
2. **Be specific in test descriptions** for better results
3. **Enable screenshots** to see what happened: `captureScreenshots: true`
4. **Use agent mode** for multi-step workflows
5. **Check results** after each test to verify success

---

## 🔑 Configuration Checklist

- [ ] Installed dependencies: `npm install`
- [ ] Created `.env` file with `OPENROUTER_API_KEY`
- [ ] Added to MCP client config (Claude/Cursor)
- [ ] Restarted MCP client
- [ ] Verified tools are available

---

## 📝 Test Result Structure

```json
{
  "runId": "run_1_timestamp",
  "url": "https://example.com",
  "test": "click the login button",
  "mode": "observe_act" | "agent",
  "success": true | false,
  "startTime": "ISO timestamp",
  "endTime": "ISO timestamp",
  "screenshots": [
    {
      "filename": "step_step1.png",
      "filepath": "/path/to/screenshot",
      "step": 1,
      "url": "https://example.com"
    }
  ],
  "testResults": {
    "observations": [...],
    "actions": [...]
  },
  "analysis": {
    "visionCritique": "AI analysis of UI...",
    "summary": "Overall test summary..."
  }
}
```

---

## 🚨 Common Errors

| Error | Solution |
|-------|----------|
| "OPENROUTER_API_KEY not set" | Add API key to MCP config |
| "Tool not found" | Restart MCP client |
| "Browser failed to start" | Install Playwright: `npx playwright install` |
| "No screenshots captured" | Set `captureScreenshots: true` |

---

## 📚 More Information

- Full documentation: `README.md`
- Setup guide: `SETUP.md`
- Source code: `src/`

---

**Happy Testing!** 🚀
