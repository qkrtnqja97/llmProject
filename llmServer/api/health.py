# llmServer/api/health.py
# LLM 서버의 상태를 확인하는 헬스 체크 엔드포인트 정의

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/health")
async def health(request: Request):
    model_loaded = hasattr(request.app.state, "model")

    return {
        "status": "ok" if model_loaded else "error",
        "model_loaded": model_loaded
    }
