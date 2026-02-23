# llmServer/app/services/llm_service.py

from app.providers.registry import ProviderRegistry
from app.schemas.chat import ChatMessage
from app.core.config import settings


class LLMService:

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry
        # 🔥 기본 모델 지정 (사용자 선택 없음, 내부에서 관리)
        self.default_model_name = "gemini-2.5-flash"

    async def generate(self, prompt: str) -> str:
        """
        프론트에서 받은 prompt를 바탕으로 LLM에게 요청
        - 메시지 리스트는 내부에서 system/user로 구성
        - 모델은 default_model_name 사용
        """
        # 1️⃣ provider 선택
        provider = self._select_provider(prompt)

        # 2️⃣ 메시지 생성 (system + user)
        messages = [
            ChatMessage(
                role="system",
                content=settings.DEFAULT_SYSTEM_PROMPT,
            ),
            ChatMessage(
                role="user",
                content=prompt,
            ),
        ]

        # 3️⃣ generate 호출
        return await provider.generate(messages)

    def _select_provider(self, prompt: str):
        """
        🔥 현재는 기본 모델만 사용
        - 추후 프롬프트 분석해서 모델 선택 로직 확장 가능
        """
        return self.registry.get_llm(self.default_model_name)