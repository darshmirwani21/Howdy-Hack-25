import uvicorn
from fastapi import FastAPI, APIRouter, Depends
from fastapi_utils.cbv import cbv
from openai_messages.messages import ChatCompletionRequest, ChatCompletionResponse

router = APIRouter()
@cbv(router)
class LLMBackendServer:
    @router.get("/")
    def read_root(self):
        return {"message": "LLM Backend is running"}

    @router.post("/v1/chat/completions")
    def chat_completions(self, request: ChatCompletionRequest):
        # TODO: Return Computer Use formatted response from OpenRouter
        return ChatCompletionResponse(
            id=request.id,
            object="chat.completion",
            created=request.created,
            model=request.model,
            choices=request.choices
        )

if __name__ == "__main__":
    app = FastAPI()
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=443)
