# backend/app/services/chat_service.py
# 채팅 로직을 처리하는 서비스 클래스 정의

from app.clients.llm_client import LLMClient

class ChatService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def chat(self, prompt: str):
        return await self.llm_client.generate(prompt)
