LLM_BACKEND_IMAGE_NAME = llm_backend
LLM_BACKEND_PORT = 8000

env:
	cat backend/llm_backend/.env.example >> backend/llm_backend/.env

build:
	docker build -t $(LLM_BACKEND_IMAGE_NAME) backend/llm_backend

run:
	docker run -d -p $(LLM_BACKEND_PORT):$(LLM_BACKEND_PORT) $(LLM_BACKEND_IMAGE_NAME)

up: build run

down:
	docker stop $(LLM_BACKEND_IMAGE_NAME) || true
	docker rm $(LLM_BACKEND_IMAGE_NAME) || true

dev: build
	docker run -d --rm -p $(LLM_BACKEND_PORT):$(LLM_BACKEND_PORT) $(LLM_BACKEND_IMAGE_NAME)
