# backend/app/schemas/chat.py
# 채팅 요청과 응답을 위한 Pydantic 모델 정의

from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

