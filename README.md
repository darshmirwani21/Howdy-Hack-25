# Meet Lumen! We give your AI the ability to see.

**The Ultimate AI-Powered Browser Testing Platform**

Meet Lumen, an advanced browser testing tool that lets AI take control of your browser, providing continuous, useful, feedback on websites being developed. Lumen interfaces with Cursor and various other IDE's to allow them to run tests on their code, iterating on the design and functional feedback.
In essence, we prevent bugs in AI generated code.

## Why we're revolutionizing unit testing

###  **Multi-Model AI Architecture**
- **OpenRouter Integration**: Access 100+ AI models including GPT-4o, Claude, Gemini, and more. We engineered a custom solution that allows OpenRouter, with FREE models, to interact with stagehand.
- **Intelligent Model Selection**: Automatically choose the best model for your specific testing needs.
- **Vision Model Analysis**: Pixel-perfect UI critique and visual regression detection

###  **Universal IDE Integration**
- **VS Code**: Seamless integration with your favorite editor
- **Cursor**: Automatically detects and integrates with Cursor's AI workflow
- **JetBrains**: Works with IntelliJ, WebStorm, PyCharm
- **Terminal**: Command-line interface for CI/CD pipelines
- **Any Editor**: Works with any development environment

###  **Advanced Testing Capabilities**
- **Observe + Act Pattern**: Revolutionary two-phase testing approach
- **Real-time Visual Analysis**: Live AI critique of UI changes
- **Screenshot Automation**: Intelligent capture on every page navigation
- **Multi-step Workflows**: Complex user journey testing
- **Visual Regression Detection**: Catch UI bugs before they reach production

##  Quick Start - MCP
- **MCP Functionality**: Lumen is also an MCP server, accessible to Copilot and Windsurf via the MCP Store!
- **Download**: Download the repo, and set the path to where you put it.
- **Add it in**: Just paste in the custom JSON into your MCP directory:
- "lumen": {
      "command": "node",
      "args": ["/Users/arjunbabla/GitHub/Howdy-Hack-25/mcp-server/src/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-your-key-here"
      }
    }
- **Finished**: Add in your key, and done!

##  Quick Start - Terminal

### 1. **Install Dependencies**
```bash
npm install
```

### 2. **Set Your API Key**
```bash
echo "OPENROUTER_API_KEY=your_key_here" > .env
```

### 3. **Run Your First Test**
```bash
node src/runner.js --url https://your-site.com --test "click login button" --screenshots --ui
```

**That's it!**  Lumen will automatically:
- Navigate to your site
- Execute the test using AI
- Capture screenshots
- Analyze the UI
- Generate a comprehensive report
- Auto-close when done

## Installation & Setup

### Prerequisites
- Node.js 18+ 
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/lumen-test-dashboard.git
   cd lumen-test-dashboard
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

4. **Verify Installation**
   ```bash
   node src/runner.js --url https://example.com --test "scroll down" --screenshots
   ```

## Usage Examples

### Basic Testing
```bash
# Simple action test
node src/runner.js --url https://myapp.com --test "click the signup button"

# With visual analysis
node src/runner.js --url https://myapp.com --test "navigate to pricing" --screenshots --ui
```

### Complex Multi-Step Workflows
```bash
# Multi-step user journey
node src/runner.js --url https://ecommerce.com --test "sign up, add item to cart, proceed to checkout" --agent --screenshots --ui
```

### CI/CD Integration
```bash
# Headless testing for pipelines
node src/runner.js --url https://staging.myapp.com --test "verify all navigation links work" --screenshots
```

## Command Line Options

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--url` | `-u` | Target website URL | `--url https://example.com` |
| `--test` | `-t` | Test description | `--test "click login button"` |
| `--agent` | `-a` | Enable multi-step AI agent | `--agent` |
| `--screenshots` | `-s` | Capture & analyze screenshots | `--screenshots` |
| `--ui` | | Launch visual dashboard | `--ui` |

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [Stagehand](https://github.com/browserbase/stagehand) by Browserbase
- Powered by [OpenRouter](https://openrouter.ai/) AI models
- UI framework by [Electron](https://electronjs.org/)

---

**Ready to revolutionize your testing workflow?** 

```bash
npm install && node src/runner.js --url https://your-site.com --test "your test" --screenshots --ui
```

*Lumen Test Dashboard - Where AI meets Web Testing* 🚀
