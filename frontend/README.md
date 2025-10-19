# Howdy Test Agent - Frontend

The core Python frontend file that AI agents call to perform automated testing using Stagehand.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env with your API keys:
# - OPENAI_API_KEY (required)
# - BROWSERBASE_API_KEY (for cloud testing)
# - BROWSERBASE_PROJECT_ID (for cloud testing)
```

### 3. Run Basic Test
```bash
python test_basic.py
```

### 4. Run Full Test Cycle
```bash
# With Stagehand (local)
python test_agent.py --web-port 3000 --prompt "Test the login functionality"
```

## Usage Examples

### Command Line Usage
```bash
# Basic usage
python test_agent.py

# With specific port
python test_agent.py --web-port 8080

# With direct prompt
python test_agent.py --prompt "Test form submission and validation"

# Text output instead of JSON
python test_agent.py --output text
```

### AI Agent Integration
The AI agent can call this script like:
```bash
python test_agent.py --prompt "USER_PROMPT_HERE"
```

## Core Methods

### Frontend Responsibilities:
- `initialize_stagehand()`: Configure and initialize Stagehand for LOCAL mode
- `get_ai_prompt()`: Get testing instructions from AI agent
- `agent_method(prompt)`: Process AI prompt into test scenarios  
- `stagehand_method(scenarios)`: Make `stagehand.agent()` calls
- `observe_method(port)`: Use `stagehand.observe()` to observe web app
- `create_live_server_connection()`: Verify web server connection

### Backend Responsibilities:
- All actual test execution logic
- Browser automation handling
- Test result processing

## Architecture

```
AI Agent → Frontend (test_agent.py) → Stagehand Agent → Backend (localhost:443)
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
