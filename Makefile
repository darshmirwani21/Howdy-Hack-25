LLM_BACKEND_IMAGE_NAME = llm_backend
LLM_BACKEND_PORT = 443

llm_backend:
	docker build -t $(LLM_BACKEND_IMAGE_NAME) backend/llm_backend
	docker run -p $(LLM_BACKEND_PORT):$(LLM_BACKEND_PORT) $(LLM_BACKEND_IMAGE_NAME)