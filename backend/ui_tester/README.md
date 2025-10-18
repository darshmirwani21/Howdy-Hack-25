# OpenRouter + Stagehand CLI Integration

A Python CLI script that configures Stagehand to use OpenRouter + DeepSeek R1T as its LLM backend, accepting natural language test instructions and executing them through Stagehand's autonomous agent.

## Prerequisites

- Python 3.8 or later
- OpenRouter account with API key
- Playwright browsers installed

## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd backend/ui_tester
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenRouter API key
   ```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Required
OPENROUTER_API_KEY=sk-or-your-api-key-here

# Optional (defaults provided)
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
STAGEHAND_MODEL=tngtech/deepseek-r1t-chimera:free
HEADLESS=false
SLOWMO_MS=0
LOG_LEVEL=info
```

### Getting OpenRouter API Key

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Navigate to your API keys section
3. Create a new API key
4. Copy the key (starts with `sk-or-`) to your `.env` file

## Usage

### Basic Examples

**Execute inline instructions:**
```bash
python stagehand_runner.py --url https://example.com --instructions "Click the login button"
```

**Execute instructions from file:**
```bash
python stagehand_runner.py --file demo_instructions.txt
```

**Run in headless mode:**
```bash
python stagehand_runner.py --headless --instructions "Navigate to /dashboard"
```

**With custom slowmo:**
```bash
python stagehand_runner.py --slowmo 1000 --instructions "Fill out the contact form"
```

### Command Line Options

- `--instructions, -i`: Natural language instructions to execute
- `--file, -f`: Path to file containing instructions (one per line)
- `--url, -u`: Base URL to navigate to before executing instructions
- `--headless`: Run browser in headless mode (default: headed)
- `--slowmo`: Slow down operations by specified milliseconds

### Instruction Format

Instructions can be provided as:
- **Inline string**: `"Click the submit button"`
- **File with newlines**: One instruction per line
- **Semicolon-separated**: `"Navigate to /login; Click sign in; Enter credentials"`

### Example Instructions

```bash
# Simple navigation and interaction
python stagehand_runner.py --instructions "Go to https://github.com and click the 'Sign in' button"

# Multi-step workflow
python stagehand_runner.py --file demo_instructions.txt

# Form filling
python stagehand_runner.py --url https://example.com --instructions "Fill out the contact form with test data"
```

## Demo

Try the included demo:

```bash
python stagehand_runner.py --file demo_instructions.txt
```

This will:
1. Navigate to https://example.com
2. Click the 'More information' link
3. Extract the page title
4. Take a screenshot

## Troubleshooting

### Common Issues

**"OPENROUTER_API_KEY environment variable is required"**
- Make sure you've created a `.env` file with your OpenRouter API key
- Verify the key is valid and has sufficient credits

**"Failed to initialize Stagehand"**
- Check your internet connection
- Verify the OpenRouter API key is correct
- Ensure the model name is valid

**Playwright browser not found**
- Run `playwright install chromium`
- On Linux, you may need additional dependencies: `playwright install-deps`

**Browser doesn't open (headed mode)**
- Check if you're running in a headless environment
- Try `--headless` flag if you can't see the browser
- On Linux servers, you may need X11 forwarding

### Debug Mode

Enable verbose logging:
```bash
LOG_LEVEL=DEBUG python stagehand_runner.py --instructions "test"
```

### Performance Tips

- Use `--headless` for faster execution
- Add `--slowmo` to slow down actions for debugging
- Keep instructions simple and specific

## Architecture

This tool integrates:
- **Stagehand**: AI-powered browser automation
- **OpenRouter**: LLM API gateway with DeepSeek R1T model
- **Playwright**: Browser automation engine
- **Python CLI**: Command-line interface for easy integration

The flow:
1. Parse natural language instructions
2. Initialize Stagehand with OpenRouter backend
3. Execute instructions using Stagehand's autonomous agent
4. Log results and handle errors gracefully

## Contributing

This is part of a larger UI testing automation project. The CLI provides a simple interface for Cursor/agents to trigger browser automation tests using natural language instructions.
