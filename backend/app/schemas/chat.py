# backend/app/schemas/chat.py
# 채팅 요청과 응답을 위한 Pydantic 모델 정의

from typing import Dict
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    prompt: str

class ChatResponse(BaseModel):
    final_answer: str
    sql_query: str | None = None  # 없을 수도 있으니
    retry_count: int
    timings: Dict[str, float]

class SessionClearRequest(BaseModel):
    session_id: str

