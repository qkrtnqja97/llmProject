# backend/app/main.py
# FastAPI 애플리케이션의 진입점입니다. 애플리케이션을 초기화하고 라우터를 등록합니다.

from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.api.v1.router import router as v1_router

app = FastAPI(lifespan=lifespan)

app.include_router(v1_router, prefix="/api/v1")
