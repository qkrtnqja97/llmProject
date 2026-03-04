# backend/app/services/chat_service.py
# 채팅 로직을 처리하는 서비스 클래스 정의

from app.clients.ai.llm_client import LLMClient
from app.repositories.inventory_repository import InventoryRepository

class ChatService:
    def __init__(self, llm_client: LLMClient, inventory_repo: InventoryRepository):
        self.llm_client = llm_client
        self.inventory_repo = inventory_repo

    async def chat(self, user_id: str, session_id: str, prompt: str):
        # 1. 재고 관련 질문인 경우 컨텍스트 생성
        if "재고" in prompt or "현황" in prompt:
            stock_data = await self.inventory_repo.get_all_inventory()

            context_prompt = f"""
            현재 재고 데이터: {stock_data}
            사용자 질문: {prompt}
            위 데이터를 바탕으로 친절하게 답변해줘.
            """
            return await self.llm_client.generate(context_prompt, user_id=user_id, session_id=session_id)

        # 2. 일반 질문 쮘리
        return await self.llm_client.generate(prompt, user_id=user_id, session_id=session_id)

    async def clear_session(self, session_id: str):
        await self.llm_client.clear_session(session_id)

    async def llm_health_check(self):
        return await self.llm_client.health()
