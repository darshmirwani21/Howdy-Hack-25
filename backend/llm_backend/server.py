import uvicorn
import time # --- DEVELOPMENT ---
import json
import asyncio
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
        # TODO: Return Computer Use formatted response from OpenRouter
        # --- DEVELOPMENT ---
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Clicking button",
                    "tool_calls": [{
                        "id": f"call_{int(time.time())}",
                        "type": "function",
                        "function": {
                            "name": "computer",
                            "arguments": json.dumps({
                                "action": "left_click",
                                "coordinate": [200, 300]
                            })
                        }
                    }]
                },
                "finish_reason": "tool_calls"
            }]
        }

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=443)
