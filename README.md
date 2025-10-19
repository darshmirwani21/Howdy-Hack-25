# Howdy Hack 25 - Stagehand Testing Tool

AI-powered browser automation testing tool for Cursor IDE integration.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Set up your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Run CLI test
node index.js --url "https://example.com" --prompt "Scroll down. Click the more information link"

# Or launch the visual UI
npm run ui
```

## ✨ Features

- **Multi-Action Testing**: Natural language prompts parsed into sequential actions
- **Automatic Observation**: Captures page state after each action
- **Screenshot Capture**: Visual verification of every step
- **Dual Interface**: CLI for automation, Electron UI for visual feedback
- **Cursor Integration**: Designed to be called by Cursor AI for automated testing
- **Comprehensive Results**: JSON + text output with observations and screenshots

## 📖 Documentation

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for complete documentation.

## 🎯 Usage Examples

### CLI Mode
```bash
# Single action
node index.js --url "http://localhost:3000" --action "click submit"

# Multi-action workflow
node index.js --url "http://localhost:3000" --prompt "Navigate to login. Fill username. Click submit"

# Verbose output
node index.js --url "http://localhost:3000" --prompt "Test checkout" --verbose
```

### UI Mode
```bash
npm run ui
```
Then enter your URL and test prompt in the dashboard.

## 🏗️ Architecture

```
User/Cursor → CLI/UI → Stagehand + OpenAI → Browser Actions
                                         ↓
                        Observe + Screenshot + Results
                                         ↓
                        JSON + Text + Visual Feedback
```

## 🔧 Tech Stack

- **Stagehand**: AI-powered browser automation
- **OpenAI**: GPT-4o for intelligent browser automation
- **Electron**: Cross-platform UI
- **Playwright**: Browser control
- **Node.js**: Runtime environment

## 📁 Project Structure

```
.
├── index.js              # Main CLI tool
├── electron/             # Electron UI
│   ├── main.js          # Main process
│   ├── preload.js       # IPC bridge
│   └── renderer/        # UI files
├── screenshots/          # Test screenshots
└── test-results-*.json  # Test outputs
```

## 🤝 Cursor Integration

This tool is designed to work seamlessly with Cursor AI:

1. Make changes to your web app
2. Cursor automatically calls: `node index.js --prompt "Test the changes" --url "http://localhost:3000"`
3. Tool executes tests and returns results
4. Cursor reads results and suggests fixes

See `.cursorrules` for integration configuration.

## 📝 License

ISC

## 🎓 Hackathon

Built for Howdy Hack 2025

