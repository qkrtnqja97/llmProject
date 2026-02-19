# api/test/test_routers/llm.py
# LLM 서버의 라우터를 정의하는 모듈입니다. 헬스체크와 텍스트 생성 엔드포인트를 포함합니다.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/llm", tags=["LLM"])

class ChatRequest(BaseModel):
    prompt: str

@router.get("/health")
async def llm_health():
    return {"status": "llm healthy"}

@router.post("/chat")
async def llm_chat(request: ChatRequest):
    # 🔥 지금은 그냥 테스트용 응답
    return {
        "reply": f"LLM Response to: {request.prompt}"
    }
