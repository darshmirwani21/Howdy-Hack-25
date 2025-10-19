# Lumen MCP Server

**AI-Powered Browser Testing via Model Context Protocol**

Lumen MCP Server exposes powerful browser testing capabilities to AI assistants through the Model Context Protocol (MCP). This allows AI assistants like Claude, GPT, and others to autonomously test websites, capture screenshots, and analyze UI/UX.

## 🌟 Features

- **🤖 AI-Powered Testing**: Use natural language to describe tests
- **🎯 Observe + Act Pattern**: Smart element detection and interaction
- **🚀 Autonomous Agent Mode**: Multi-step workflows handled automatically
- **📸 Screenshot Capture**: Automatic screenshot capture on navigation
- **👁️ Vision AI Analysis**: UI/UX critique using GPT-4 Vision
- **🔌 MCP Integration**: Seamlessly integrates with any MCP-compatible AI assistant

## 📋 Available Tools

### 1. `run_browser_test`
Execute a single browser test action using the Observe + Act pattern.

**Example**: "Click the login button", "Fill out the contact form"

### 2. `run_agent_test`
Execute multi-step autonomous browser tests using Computer Use Agent mode.

**Example**: "Sign up for an account and verify email", "Complete checkout process"

### 3. `analyze_screenshot`
Analyze UI screenshots with vision AI for design and UX feedback.

### 4. `get_test_results`
Retrieve detailed results from previous test runs.

### 5. `list_test_runs`
List all executed test runs with summary information.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd mcp-server
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

Get your OpenRouter API key from: https://openrouter.ai/

### 3. Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "lumen": {
      "command": "node",
      "args": ["/absolute/path/to/Howdy-Hack-25/mcp-server/src/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**For Cursor** (`.cursor/mcp.json` in your workspace):

```json
{
  "mcpServers": {
    "lumen": {
      "command": "node",
      "args": ["./mcp-server/src/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 4. Restart Your MCP Client

Restart Claude Desktop or Cursor to load the MCP server.

## 💡 Usage Examples

Once configured, you can ask your AI assistant:

### Basic Testing
```
"Use Lumen to test clicking the login button on https://example.com"
```

### Multi-Step Workflows
```
"Run an agent test on https://myapp.com to sign up for an account"
```

### UI Analysis
```
"Analyze the screenshot at /path/to/screenshot.png for UX issues"
```

### Get Results
```
"Show me the results from the last browser test"
```

## 🛠️ Architecture

```
mcp-server/
├── src/
│   ├── index.js              # MCP server entry point
│   ├── browser-manager.js    # Stagehand wrapper & AI analysis
│   ├── test-executor.js      # Test execution logic
│   ├── screenshot-handler.js # Screenshot management
│   ├── tools.js              # MCP tool definitions
│   └── resources.js          # MCP resource handlers
├── package.json
├── .env.example
└── README.md
```

## 🔧 Configuration

### Environment Variables

- `OPENROUTER_API_KEY` (required): Your OpenRouter API key
- `STAGEHAND_MODEL` (optional): AI model to use (default: `openai/gpt-4o-mini`)

### Supported Models

- `openai/gpt-4o-mini` (default, free)
- `openai/gpt-4o`
- `anthropic/claude-3-5-sonnet`
- `google/gemini-pro`
- And 100+ more via OpenRouter

## 📊 Resources

The MCP server exposes resources for accessing test data:

- `test-run://{runId}` - Complete test run data
- `screenshot://{runId}/{step}` - Individual screenshots
- `test-runs://list` - List of all test runs

## 🐛 Debugging

Enable verbose logging:

```bash
# Run the server directly to see logs
node src/index.js
```

The server logs to stderr, so you'll see diagnostic information while it runs.

## 🤝 Integration with Lumen CLI

This MCP server is built on the same core as the Lumen CLI tool. You can use both:

- **MCP Server**: For AI assistant integration
- **CLI Tool**: For manual testing and development

Both share the same testing engine and capabilities.

## 📝 License

MIT License - see parent project LICENSE file

## 🙏 Acknowledgments

- Built on [Stagehand](https://github.com/browserbase/stagehand) by Browserbase
- Powered by [OpenRouter](https://openrouter.ai/) AI models
- Uses [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic

---

**Ready to supercharge your AI assistant with browser testing?** 🚀

Install the dependencies and configure your MCP client to get started!
