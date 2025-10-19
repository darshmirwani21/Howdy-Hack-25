# Testing Guide

## Understanding the Test Files

### **test_basic.py** - Test WITHOUT Web App
- ✅ Tests internal methods and data flow
- ✅ No Stagehand initialization required
- ✅ No web app required
- ✅ No backend required
- ✅ Tests prompt parsing, data storage, fallback simulation

### **test_agent.py** - Full Integration Test
- ⚠️ Requires Stagehand initialization
- ⚠️ Requires web app running on port 3000
- ⚠️ Requires backend running on port 443 (optional)
- ⚠️ Requires OPENAI_API_KEY in .env
- ✅ Tests full agent execution with real browser

## Quick Start Testing

### **1. Test Basic Functionality (No Setup Required)**
```bash
cd frontend
python test_basic.py
```

**What it tests:**
- ✅ Agent instance creation
- ✅ Prompt parsing into test scenarios
- ✅ Data storage (execution_results, screenshots, observations)
- ✅ Fallback simulation mode
- ✅ Backend API connection check
- ✅ Web server connection check
- ✅ Payload preparation and JSON serialization

**Expected Output:**
```
🧪 Testing Howdy Test Agent (Basic Functionality)
============================================================
NOTE: This tests internal methods WITHOUT Stagehand/web app
============================================================

✅ Agent instance created
   Web port: 3000
   Backend port: 443
   Screenshots directory created: ./screenshots/

1️⃣  Testing prompt parsing...
   Prompt: 'Test the login functionality'
   → Generated 4 scenarios
   ...

✅ Basic functionality test completed!
```

### **2. Test Stagehand Initialization (Requires API Key)**
```bash
cd frontend
python test_basic.py --with-stagehand
```

**Prerequisites:**
- OPENAI_API_KEY in .env file
- Stagehand installed: `pip install stagehand`

**What it tests:**
- ✅ Stagehand initialization
- ✅ Browser launch
- ✅ Configuration validation

### **3. Test Full Cycle (Requires Everything)**
```bash
cd frontend
python test_agent.py --prompt "Test the login functionality"
```

**Prerequisites:**
- ✅ Web app running on port 3000
- ✅ Backend running on port 443 (optional)
- ✅ OPENAI_API_KEY in .env
- ✅ Stagehand installed

**What it tests:**
- ✅ Full test cycle with real browser
- ✅ Agent execution with Stagehand
- ✅ Screenshot capture
- ✅ Backend communication
- ✅ Result aggregation

## Testing Scenarios

### **Scenario 1: Just Installed - Verify Setup**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run basic test
python test_basic.py
```

**Expected:** All tests pass except backend/web server connection (expected to fail)

### **Scenario 2: Have API Key - Test Stagehand**
```bash
# 1. Create .env file
cp env_example.txt .env
# Edit .env with your OPENAI_API_KEY

# 2. Install Stagehand
pip install stagehand

# 3. Test Stagehand initialization
python test_basic.py --with-stagehand
```

**Expected:** Stagehand initializes successfully, browser launches

### **Scenario 3: Have Web App - Full Integration**
```bash
# 1. Start your web app on port 3000
# 2. (Optional) Start backend on port 443

# 3. Run full test
python test_agent.py --prompt "Test the homepage"
```

**Expected:** Agent navigates to localhost:3000, executes tests, returns results

### **Scenario 4: Test Public Website**
```bash
# No local web app needed!
python test_agent.py --prompt "Navigate to https://example.com and click links"
```

**Expected:** Agent navigates to example.com, executes tests

## Troubleshooting

### **Error: "StagehandConfig is not defined"**
**Fix:** Already fixed - `from stagehand.config import StagehandConfig` added

### **Error: "Failed to initialize Stagehand"**
**Cause:** Missing OPENAI_API_KEY
**Fix:** 
```bash
cp env_example.txt .env
# Edit .env and add: OPENAI_API_KEY=your_key_here
```

### **Error: "Cannot connect to web server"**
**Cause:** No web app running on port 3000
**Fix:** Either:
1. Start your web app on port 3000, OR
2. Test with public website: `--prompt "Navigate to https://example.com"`

### **Error: "Cannot connect to backend"**
**Cause:** Backend not running on port 443
**Fix:** This is OK! Backend is optional. Tests will still run.

### **Fallback Simulation Mode**
If Stagehand fails to initialize, the agent automatically falls back to simulation mode:
- ✅ Tests still run
- ✅ Simulated results generated
- ⚠️ No real browser automation
- ⚠️ No real screenshots

## What Each Test Validates

### **test_basic.py** validates:
1. ✅ Class instantiation
2. ✅ Directory creation (./screenshots/)
3. ✅ Prompt parsing logic
4. ✅ Data structure initialization
5. ✅ Fallback simulation
6. ✅ Connection checking
7. ✅ Payload structure
8. ✅ JSON serialization

### **test_agent.py** validates:
1. ✅ Stagehand initialization
2. ✅ Browser launch
3. ✅ Agent creation
4. ✅ Agent execution
5. ✅ Screenshot capture
6. ✅ Data storage
7. ✅ Backend communication
8. ✅ Result aggregation

## Recommended Testing Order

1. **First:** `python test_basic.py` - Verify code works
2. **Second:** `python test_basic.py --with-stagehand` - Verify Stagehand setup
3. **Third:** `python test_agent.py --prompt "Navigate to https://example.com"` - Test with public site
4. **Finally:** `python test_agent.py --prompt "Test login"` - Test with your web app

## Summary

| Test | Web App | Backend | API Key | Stagehand | Purpose |
|------|---------|---------|---------|-----------|---------|
| `test_basic.py` | ❌ | ❌ | ❌ | ❌ | Verify code |
| `test_basic.py --with-stagehand` | ❌ | ❌ | ✅ | ✅ | Verify setup |
| `test_agent.py` (public site) | ❌ | ❌ | ✅ | ✅ | Test browser |
| `test_agent.py` (your app) | ✅ | ⚠️ | ✅ | ✅ | Full integration |

✅ = Required
⚠️ = Optional
❌ = Not needed

