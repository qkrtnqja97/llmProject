# backend/app/api/v1/health.py
# API 버전 1의 헬스 체크 라우터를 정의하는 모듈입니다. 시스템과 머신러닝 서버의 상태를 확인하는 엔드포인트를 제공합니다.

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import get_llm_client
from app.clients.llm_client import LLMClient

router = APIRouter(prefix="/health", tags=["health"])


# 🔹 1. 백엔드 서버 상태
@router.get("")
async def backend_health():
    return {
        "status": "ok",
        "backend": True,
    }


# 🔹 2. LLM 서버 상태
@router.get("/llm")
async def llm_health(llm_client: LLMClient = Depends(get_llm_client)):
    llm_ok = await llm_client.health()

    if not llm_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "llm_server": False,
            },
        )

    return {
        "status": "ok",
        "llm_server": True,
    }
