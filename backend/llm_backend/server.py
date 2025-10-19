import uvicorn
import time # --- DEVELOPMENT ---
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends
from fastapi_utils.cbv import cbv
from openai_messages.messages import ChatCompletionRequest

router = APIRouter()
@cbv(router)
class LLMBackendServer:
    @router.get("/")
    def read_root(self):
        return {"message": "LLM Backend is running"}
    
    @router.get("/v1")
    def read_v1(self):
        return {"message": "LLM Backend v1 is running"}

    @router.post("/v1/chat/completions")
    def chat_completions(self, request: ChatCompletionRequest):
        # Return proper OpenAI-compatible chat completion response
        # Stagehand expects standard OpenAI format
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "action": "click",
                        "selector": "button",
                        "reasoning": "Clicking the button as requested"
                    })
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(app, host="0.0.0.0", port=8000)
