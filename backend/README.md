# Browser Automation Testing System

Automated browser testing using Stagehand (agent mode) with OpenRouter's DeepSeek model.

## Architecture

```
CLI Script → Stagehand (agent mode) → FastAPI Backend → OpenRouter (DeepSeek) → Browser Actions
```

## Prerequisites

- Docker and Docker Compose
- `.env` file in the `backend/` directory with:
  ```bash
  OPENROUTER_API_KEY=your_key_here
  STAGEHAND_MODEL=tngtech/deepseek-r1t-chimera:free
  STAGEHAND_API_URL=http://localhost:443
  ```
- Application running on `localhost:3000` (accessible from Docker as `host.docker.internal:3000`)

## Setup

1. Create your `.env` file in the `backend/` directory:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your actual values
   ```

2. Build the Docker container:
   ```bash
   docker-compose build
   ```

3. Start the FastAPI backend:
   ```bash
   docker-compose up -d
   ```

## Usage

### Running Tests from CLI

Run automated tests by providing a detailed AI-generated changelog:

```bash
docker-compose exec stagehand-backend python /app/stagehand_runner.py "Test the login functionality after recent authentication module changes. Verify that users can successfully log in with valid credentials and see appropriate error messages for invalid ones."
```

### Example Test Descriptions

**Basic Navigation Test:**
```bash
docker-compose exec stagehand-backend python /app/stagehand_runner.py "Navigate to the homepage, verify all navigation links are present and functional, and ensure the footer displays correctly."
```

**Form Submission Test:**
```bash
docker-compose exec stagehand-backend python /app/stagehand_runner.py "Test the contact form submission. Fill in all required fields with valid data, submit the form, and verify a success message appears."
```

**Complex User Flow:**
```bash
docker-compose exec stagehand-backend python /app/stagehand_runner.py "Perform a complete user registration flow: navigate to signup page, fill in username, email, and password, submit the form, verify account creation confirmation, then test logging in with the new credentials."
```

## How It Works

1. **FastAPI Backend** (`llm_backend/server.py`):
   - Runs on port 443
   - Acts as an OpenAI-compatible proxy
   - Forwards requests to OpenRouter's DeepSeek model

2. **Stagehand Runner** (`stagehand_runner.py`):
   - Accepts natural language test descriptions via CLI
   - Initializes Stagehand in LOCAL mode (headed browser)
   - Uses Stagehand's agent mode for autonomous multi-step testing
   - Targets `http://host.docker.internal:3000`

3. **OpenRouter Integration**:
   - Model: `tngtech/deepseek-r1t-chimera:free`
   - No cost for API calls
   - Provides LLM reasoning for browser automation

## Debugging

### View Logs
```bash
docker-compose logs -f stagehand-backend
```

### Access Container Shell
```bash
docker-compose exec stagehand-backend /bin/bash
```

### Test FastAPI Backend
```bash
curl http://localhost:443/
```

## Troubleshooting

**Issue: Can't connect to localhost:3000**
- Ensure your app is running on port 3000
- Docker uses `host.docker.internal` to access host machine

**Issue: OpenRouter API errors**
- Verify `OPENROUTER_API_KEY` is set correctly in `.env`
- Check OpenRouter service status

**Issue: Browser doesn't display in headed mode**
- Xvfb is running in the container for virtual display
- Check `DISPLAY=:99` environment variable

## Files

- `llm_backend/server.py` - FastAPI backend (OpenRouter proxy)
- `stagehand_runner.py` - CLI script for running tests
- `llm_backend/Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker orchestration
- `llm_backend/requirements.txt` - Python dependencies

