# backend/app/api/v1/chat.py
# 채팅 API 엔드포인트 정의

from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest
from app.api.deps import get_chat_service
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/")
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    result = await service.chat(request.prompt)
    return result
