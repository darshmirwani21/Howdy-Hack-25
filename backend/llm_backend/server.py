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


class OpenRouterClient:
    """Handles all OpenRouter API interactions"""
    
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.default_model = os.getenv("STAGEHAND_MODEL")
        self.timeout = 180.0
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured in environment")
        if not self.default_model:
            raise ValueError("STAGEHAND_MODEL not configured in environment")
    
    def _build_request_payload(self, request: ChatCompletionRequest) -> dict:
        """Build OpenRouter API request payload from ChatCompletionRequest"""
        # Use model from environment or fall back to request model
        model = self.default_model if self.default_model else request.model
        
        # Base payload
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        }
        
        # Add optional parameters if provided
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.response_format is not None:
            payload["response_format"] = request.response_format
        if request.tools is not None:
            payload["tools"] = [tool.model_dump() for tool in request.tools]
        if request.tool_choice is not None:
            payload["tool_choice"] = request.tool_choice
        
        return payload
    
    async def chat_completion(self, request: ChatCompletionRequest) -> dict:
        """Send chat completion request to OpenRouter and return response"""
        payload = self._build_request_payload(request)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"OpenRouter API error: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling OpenRouter: {str(e)}"
                )


# Initialize OpenRouter client
openrouter_client = OpenRouterClient()

router = APIRouter()
@cbv(router)
class LLMBackendServer:
    @router.get("/")
    def read_root(self):
        return {"message": "LLM Backend is running"}

    @router.post("/v1/chat/completions")
    async def chat_completions(self, request: ChatCompletionRequest):
        """Proxy chat completion requests to OpenRouter"""
        return await openrouter_client.chat_completion(request)

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=443)
