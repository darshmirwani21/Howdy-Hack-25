# Stagehand Browser Automation

Simple AI-powered browser testing using Stagehand (Node.js) with OpenRouter.

## Prerequisites

- Docker and Docker Compose
- OpenRouter API key

## Setup

1. **Create `.env` file** in the `backend/` directory:

```bash
OPENROUTER_API_KEY=your-api-key-here
STAGEHAND_MODEL=openai/gpt-4o-mini
```

2. **Build the Docker container**:

```bash
docker-compose build
```

3. **Start the container**:

```bash
docker-compose up -d
```

## Usage

Run tests with **2 required flags** + **1 optional flag**:
- `--url` or `-u`: Target URL
- `--test` or `-t`: Test description
- `--agent` or `-a`: (Optional) Use Computer Use Agent mode

```bash
node runner.js --url "<URL>" --test "<what to test>" [--agent]
```

### Two Modes

**Normal Mode (without `--agent`)** - Single action:
```bash
node runner.js --url "https://example.com" --test "Click the login button"
```
- Uses `page.act()` for single, precise actions
- Fast and efficient
- Good for known, specific tasks

**Computer Use Agent Mode (with `--agent`)** - Multi-step autonomous:
```bash
node runner.js --url "https://example.com" --test "Navigate to pricing and compare all plans" --agent
```
- Uses `stagehand.agent()` for complex, multi-step tasks
- AI figures out multiple steps autonomously
- Good for exploratory or complex workflows

### Examples

**Normal Mode - Click a button:**
```bash
node runner.js \
  --url "https://github.com/browserbase/stagehand" \
  --test "Click the star button"
```

**Normal Mode - Fill a form field:**
```bash
node runner.js \
  --url "https://example.com/login" \
  --test "Type 'test@example.com' into the email field"
```

**Agent Mode - Multi-step exploration:**
```bash
node runner.js \
  --url "https://github.com/browserbase/stagehand" \
  --test "Find the star count and latest release version" \
  --agent
```

**Agent Mode - Complex workflow:**
```bash
node runner.js \
  --url "https://example.com" \
  --test "Navigate to pricing, find the enterprise plan, and extract all features" \
  --agent
```

## How It Works

1. **Stagehand** (Node.js version) - Real implementation with LOCAL mode support
2. **Two Modes:**
   - **Normal Mode**: Single actions with `page.act()`
   - **Computer Use Agent Mode**: Multi-step autonomous with `stagehand.agent()`
3. **OpenRouter** - Provides LLM capabilities (no OpenAI key needed)
4. **Playwright** - Handles actual browser automation
5. **Docker** - Runs everything in a container with Xvfb for headed mode

## Configuration

All configuration is done via environment variables in `.env`:

- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)
- `STAGEHAND_MODEL` - Model to use (default: `openai/gpt-4o-mini`)

### Recommended Models

**Paid (best quality):**
- `openai/gpt-4o-mini` (cheap and good)
- `openai/gpt-4o` (best quality)
- `anthropic/claude-3.5-sonnet`

**Free (for testing):**
- `google/gemini-2.0-flash-exp:free`
- `tngtech/deepseek-r1t-chimera:free`

## Troubleshooting

**Check container logs:**
```bash
docker-compose logs stagehand
```

**Access container shell:**
```bash
docker-compose exec stagehand sh
```

**Rebuild after changes:**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Architecture

```
CLI (2 flags) → Stagehand (LOCAL mode) → OpenRouter API → Browser Actions
```

- **No Browserbase** - Runs locally in Docker
- **No hardcoded values** - All config in .env
- **Simple CLI** - Just URL and test description
- **Clean setup** - Minimal dependencies
