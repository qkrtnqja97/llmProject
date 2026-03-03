# backend/app/services/chat_service.py
# 채팅 로직을 처리하는 서비스 클래스 정의

from app.clients.ai.llm_client import LLMClient
from app.repositories.inventory_repository import InventoryRepository

class ChatService:
    def __init__(self, llm_client: LLMClient, inventory_repo: InventoryRepository):
        self.llm_client = llm_client
        self.inventory_repo = inventory_repo

    async def chat(self, prompt: str):
        # 1. 사용자의 질문에 "재고"나 "제품" 키워드가 있는지 확인 (간단한 예시)
        if "재고" in prompt or "현황" in prompt:
            # DB에서 실제 재고 데이터를 가져옴
            stock_data = await self.inventory_repo.get_all_inventory()
            # AI에게 줄 컨텍스트 생성
            context_prompt = f"현재 재고 데이터: {stock_data}\n사용자 질문: {prompt}\n위 데이터를 바탕으로 친절하게 답변해줘."
            return await self.llm_client.generate(context_prompt)
        
        # 2. 일반 질문은 그대로 진행
        return await self.llm_client.generate(prompt)