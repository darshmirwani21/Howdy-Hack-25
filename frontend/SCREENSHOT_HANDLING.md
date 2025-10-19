# Screenshot Handling - Optimized Implementation

## Changes Made

### **Before:**
- Took manual screenshots with `page.screenshot()`
- Duplicate screenshots (manual + auto)
- Had to upload files separately

### **After:**
- Uses Stagehand's built-in `autoScreenshot: True`
- No duplicate screenshots
- Screenshots embedded in `agent_result`
- Sent as part of JSON payload

## How It Works Now

### **1. Screenshot Capture:**
```python
# Stagehand automatically takes screenshots
agent_result = await agent.execute({
    'instruction': scenario,
    'autoScreenshot': True,  # Stagehand handles screenshots
    'maxSteps': 20,
    'waitBetweenActions': 500
})

# Extract screenshot references from result
if 'screenshots' in agent_result:
    screenshots = agent_result.get('screenshots', [])
    self.screenshots.append(screenshots[-1])
```

### **2. Screenshot Data in Result:**
```python
# agent_result contains:
{
    "success": true,
    "actions": [...],
    "screenshots": [
        "base64_encoded_image_data",  # or path/URL
        "base64_encoded_image_data",
        ...
    ],
    "messages": [...]
}
```

### **3. Send to Backend:**
```python
# Screenshots are already in execution_results
payload = {
    "execution_results": self.execution_results,  # Contains agent_result with screenshots
    "screenshot_references": self.screenshots,
    "observations": self.observations,
    "metadata": {...}
}

# Simple JSON POST
response = requests.post(
    f"http://localhost:{backend_port}/analyze",
    json=payload,
    timeout=30
)
```

## Backend Expectations

Your backend `/analyze` endpoint should now handle:

### **Request Format:**
- **Content-Type:** `application/json`
- **Payload Structure:**
```json
{
  "execution_results": [
    {
      "scenario": "Navigate to login page",
      "result": {
        "success": true,
        "actions": ["Navigated to /login", "Found login form"],
        "screenshots": ["base64_image_data_or_url", ...],
        "messages": [...]
      },
      "timestamp": "2025-01-01T12:00:00",
      "index": 0
    }
  ],
  "screenshot_references": ["path1", "path2", ...],
  "observations": [...],
  "metadata": {...}
}
```

### **Example Backend (FastAPI):**
```python
from fastapi import FastAPI
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    execution_results: list
    screenshot_references: list
    observations: list
    metadata: dict

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    # Access screenshots from execution_results
    for result in request.execution_results:
        agent_result = result['result']
        if 'screenshots' in agent_result:
            screenshots = agent_result['screenshots']
            # Process screenshots (base64 or URLs)
            for screenshot in screenshots:
                # Decode base64 or fetch URL
                pass
    
    return {"status": "success", "analysis": {...}}
```

## Agent Execute Arguments

### **Available Options:**
```python
agent_result = await agent.execute({
    # REQUIRED
    'instruction': str,  # Task description
    
    # OPTIONAL
    'maxSteps': int,  # Max actions (default: 20)
    'autoScreenshot': bool,  # Auto screenshots (default: True)
    'waitBetweenActions': int,  # Delay in ms (default: 0)
    'context': str,  # Additional context/constraints
})
```

### **Current Configuration:**
```python
agent_result = await agent.execute({
    'instruction': scenario,
    'maxSteps': 20,
    'autoScreenshot': True,
    'waitBetweenActions': 500
})
```

### **Recommendations:**
- ✅ Keep `autoScreenshot: True` - Stagehand handles internal screenshots
- ✅ Keep manual screenshot - Gives you explicit control
- ✅ `waitBetweenActions: 500` - Good for stability
- ✅ `maxSteps: 20` - Reasonable for most tests
- 💡 Add `context` if needed: `'context': 'Test on localhost:3000'`

## Benefits of This Approach

✅ **No Duplication** - Single source of screenshots from Stagehand
✅ **Embedded Data** - Screenshots included in agent results
✅ **Simpler Backend** - Just handle JSON, no file uploads
✅ **Better Context** - Screenshots linked to specific actions
✅ **No File Management** - No need to manage local screenshot files

## Screenshot Data Format

Stagehand may provide screenshots as:
- **Base64 encoded strings** - Embedded directly in JSON
- **URLs** - Links to stored screenshots
- **File paths** - Paths to local files

Your backend should handle all formats:

```python
def process_screenshot(screenshot_data):
    if screenshot_data.startswith('data:image'):
        # Base64 encoded
        import base64
        image_data = base64.b64decode(screenshot_data.split(',')[1])
    elif screenshot_data.startswith('http'):
        # URL
        import requests
        image_data = requests.get(screenshot_data).content
    else:
        # File path
        with open(screenshot_data, 'rb') as f:
            image_data = f.read()
    
    return image_data
```

