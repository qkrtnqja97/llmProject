# backend/app/api/v1/router.py
# API 버전 1의 라우터를 정의하는 모듈입니다. 각 기능별 라우터를 포함하여 API 엔드포인트를 구성합니다.

from app.api.v1.routes import health_router
from fastapi import APIRouter
from app.api.v1.routes import chat_router

router = APIRouter()

router.include_router(health_router.router, tags=["health"])
router.include_router(chat_router.router, tags=["chat"])