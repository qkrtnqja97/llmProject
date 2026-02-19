# backend/app/api/v1/router.py
# API 버전 1의 라우터를 정의하는 모듈입니다. 각 기능별 라우터를 포함하여 API 엔드포인트를 구성합니다.

from fastapi import APIRouter
from app.api.v1 import health, chat

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(chat.router, tags=["chat"])
