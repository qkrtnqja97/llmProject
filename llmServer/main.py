# llmServer/main.py
# LLM 모델을 로드하는 유틸리티 함수 정의

from fastapi import FastAPI
from contextlib import asynccontextmanager
from llm_server.core.model_loader import load_model
from llm_server.api import health, generate

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(generate.router)
