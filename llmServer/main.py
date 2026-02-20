# llmServer/main.py
# LLM 모델을 로드하는 유틸리티 함수 정의

from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(generate.router)
