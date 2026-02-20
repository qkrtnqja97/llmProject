# backend/app/api/deps.py
# API 엔드포인트에서 사용할 의존성 정의

from fastapi import Depends, Request
import httpx

from app.clients.ai.llm_client import LLMClient
from app.services.chat_service import ChatService


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_llm_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> LLMClient:
    return LLMClient(http_client)


def get_chat_service(
    llm_client: LLMClient = Depends(get_llm_client),
) -> ChatService:
    return ChatService(llm_client)