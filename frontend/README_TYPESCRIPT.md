# Howdy Test Agent - TypeScript Version

TypeScript port of the Python test agent with identical functionality.

## Quick Start

### 1. Install Dependencies
```bash
npm install
# or
yarn install
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env with your API keys:
# - OPENAI_API_KEY (required)
# - MODEL_API_KEY (alternative)
```

### 3. Build TypeScript
```bash
npm run build
```

### 4. Run Test Agent
```bash
# With Node.js
node dist/test_agent.js --prompt "Test the login functionality"

# With ts-node (development)
npm run dev -- --prompt "Test the login functionality"
```

## Usage Examples

### Command Line Usage
```bash
# Basic usage
node dist/test_agent.js

# With specific port
node dist/test_agent.js --web-port 8080

# With direct prompt
node dist/test_agent.js --prompt "Test form submission and validation"

# Text output instead of JSON
node dist/test_agent.js --output text
```

### Programmatic Usage
```typescript
import { HowdyTestAgent } from './test_agent';

async function runTests() {
    const agent = new HowdyTestAgent(3000, 443);
    
    try {
        await agent.initialize_stagehand();
        const results = await agent.run_full_test_cycle();
        console.log(results);
    } finally {
        await agent.close_stagehand();
    }
}

runTests();
```

## Core Methods

### Frontend Responsibilities:
- `initialize_stagehand()`: Configure and initialize Stagehand for LOCAL mode
- `get_ai_prompt()`: Get testing instructions from AI agent
- `agent_method(prompt)`: Process AI prompt into test scenarios  
- `stagehand_method(scenarios)`: Make `agent.execute()` calls
- `observe_method(port)`: Use `page.observe()` to observe web app
- `create_live_server_connection()`: Verify web server connection
- `send_to_backend_for_analysis()`: Send collected data to backend

### Backend Responsibilities:
- All actual test execution logic
- Browser automation handling
- Test result processing

## Architecture

```
AI Agent → test_agent.ts → Stagehand Agent → Backend (localhost:443)
              ↓                            ↓
        Stores Results              Web App (localhost:3000)
              ↓
        Sends to Backend
              ↓
        Backend Analysis
```

### Data Flow:
1. **Frontend** configures Stagehand for LOCAL context
2. **Frontend** gets prompts from LLM
3. **Frontend** creates agent instance and calls `agent.execute()`
4. **Agent** executes tests and returns JSON results
5. **Frontend** stores results, screenshots, observations in memory
6. **Frontend** sends all collected data to backend `/analyze` endpoint
7. **Backend** analyzes data and returns insights
8. **Frontend** returns final results to AI

### What Gets Stored in Memory:
- `execution_results[]` - All agent.execute() results (JSON)
- `screenshots[]` - Screenshot file paths
- `observations[]` - All page.observe() results

### What Gets Sent to Backend:
```json
{
  "execution_results": [...],
  "screenshot_paths": [...],
  "observations": [...],
  "metadata": {...}
}
```

## Differences from Python Version

### TypeScript-Specific:
- Uses `axios` instead of `requests`
- Uses `readline` for stdin input
- Uses `fs` and `path` for file operations
- Type-safe interfaces for all data structures
- Proper TypeScript async/await patterns

### Identical Functionality:
- ✅ All methods have same behavior
- ✅ Same data structures and flow
- ✅ Same Stagehand integration
- ✅ Same backend communication
- ✅ Same error handling patterns

## Installation

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install

# Build TypeScript
npm run build

# Run
node dist/test_agent.js --prompt "Test login functionality"
```

## Development

```bash
# Run with ts-node (no build needed)
npm run dev -- --prompt "Test login"

# Build and run
npm run build && npm start

# Type checking
npx tsc --noEmit
```

## Files

- `test_agent.ts` - Main TypeScript implementation
- `package.json` - Node.js dependencies
- `tsconfig.json` - TypeScript configuration
- `dist/` - Compiled JavaScript output

## Requirements

- Node.js >= 18.0.0
- TypeScript >= 5.3.0
- OpenAI API Key
- Playwright (installed via npm)

