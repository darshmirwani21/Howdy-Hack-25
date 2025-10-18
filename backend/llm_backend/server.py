import uvicorn
import time # --- DEVELOPMENT ---
import json
import asyncio
import os
import httpx
from dotenv import dotenv_values
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from openai_messages.messages import ChatCompletionRequest

# Load environment variables
config = dotenv_values("/app/.env")
for key, value in config.items():
    if value:
        os.environ[key] = value

router = APIRouter()
@cbv(router)
class LLMBackendServer:
    @router.get("/")
    def read_root(self):
        return {"message": "LLM Backend is running"}

    @router.post("/v1/chat/completions")
    async def chat_completions(self, request: ChatCompletionRequest):
        # Get OpenRouter API key from environment
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
        
        # Get model from environment, fallback to request model
        model = os.getenv("STAGEHAND_MODEL", request.model)
        
        # Prepare request for OpenRouter
        openrouter_request = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        }
        
        # Add optional parameters if provided
        if request.temperature is not None:
            openrouter_request["temperature"] = request.temperature
        if request.max_tokens is not None:
            openrouter_request["max_tokens"] = request.max_tokens
        if request.response_format is not None:
            openrouter_request["response_format"] = request.response_format
        if request.tools is not None:
            openrouter_request["tools"] = [tool.dict() for tool in request.tools]
        if request.tool_choice is not None:
            openrouter_request["tool_choice"] = request.tool_choice
        
        # Make request to OpenRouter
        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=openrouter_request
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=f"OpenRouter API error: {e.response.text}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error calling OpenRouter: {str(e)}")

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=443)
