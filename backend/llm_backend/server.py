from requests import request
import uvicorn
import time
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends
from fastapi_utils.cbv import cbv
from openai_messages.messages import ChatCompletionRequest
from openrouter_client import OpenRouterClient

def get_error_response(e: Exception, request: ChatCompletionRequest):
    """Generate a default error response in OpenAI format."""
    return {
        "id": f"error-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": f"Error: {str(e)}"
            },
            "finish_reason": "error"
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "error": {
            "message": str(e),
            "type": "internal_error"
        }
    }

def get_openrouter_client():
    return OpenRouterClient()

router = APIRouter()
@cbv(router)
class LLMBackendServer:
    client: OpenRouterClient = Depends(get_openrouter_client)

    @router.get("/")
    def read_root(self):
        return {"message": "LLM Backend is running"}
    
    @router.get("/v1")
    def read_v1(self):
        return {"message": "LLM Backend v1 is running"}
    
    @router.get("/v1/test")
    def test_openrouter(self, client: OpenRouterClient = Depends(get_openrouter_client)):
        """Test endpoint to verify OpenRouter connection."""
        is_connected = client.test_connection()
        return {
            "openrouter_connected": is_connected,
            "api_key_configured": client.api_key is not None,
            "base_url": client.base_url,
            "model": client.model,
            "status": "ready" if is_connected else "error"
        }

    @router.post("/v1/chat/completions")
    async def chat_completions(self, request: ChatCompletionRequest):
        """
        Proxy endpoint that forwards Stagehand requests to OpenRouter.
        Accepts OpenAI-format requests and returns OpenAI-format responses.
        """
        try:
            # Convert Pydantic models to dictionaries
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            # Forward to OpenRouter
            response = await self.client.async_chat_completion(
                messages=messages,
                model=request.model,
                temperature=request.temperature if request.temperature is not None else 0.7,
                max_tokens=request.max_tokens,
                response_format=request.response_format
            )
            
            return response
            
        except Exception as e:
            # Return error in OpenAI format
            return get_error_response(e, request)

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(app, host="0.0.0.0", port=8000)
