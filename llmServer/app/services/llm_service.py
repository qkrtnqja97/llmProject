# llmServer/app/services/llm_service.py

# llmServer/app/services/llm_service.py

import logging
import time
from typing import List

from app.providers.registry import ProviderRegistry
from app.schemas.chat import ChatMessage
from app.core.config import settings
from app.core.logging.logging_tags import LogTag
from app.core.logging.request_context import get_request_id

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

        # 🔥 기본 모델 전략 - 추후 환경변수나 이런걸로 빼자.
        self.router_model = "gemini-2.5-flash"
        self.sql_model = "gemini-2.5-flash"
        self.answer_model = "gemini-2.5-flash"

    # ==========================================================
    # 🔹 Public Use-case APIs
    # ==========================================================

    async def generate_router(self, prompt: str) -> str:
        return await self._generate_internal(
            prompt=prompt,
            model_name=self.router_model,
            system_prompt=settings.ROUTER_SYSTEM_PROMPT,
            log_tag=LogTag.ROUTER,
        )

    async def generate_sql(self, prompt: str) -> str:
        return await self._generate_internal(
            prompt=prompt,
            model_name=self.sql_model,
            system_prompt=settings.SQL_SYSTEM_PROMPT,
            log_tag=LogTag.SQL_GENERATION,
        )

    async def generate_answer(self, prompt: str) -> str:
        return await self._generate_internal(
            prompt=prompt,
            model_name=self.answer_model,
            system_prompt=settings.DEFAULT_SYSTEM_PROMPT,
            log_tag=LogTag.ANSWER,
        )

    # ==========================================================
    # 🔹 Core LLM Call
    # ==========================================================

    async def _generate_internal(
        self,
        prompt: str,
        model_name: str,
        system_prompt: str,
        log_tag: str,
    ) -> str:

        request_id = get_request_id()

        logger.info(
            "LLM generate start",
            extra={
                "tag": log_tag,
                "request_id": request_id,
                "model": model_name,
                "prompt_length": len(prompt),
            },
        )

        start = time.time()

        provider = self.registry.get_llm(model_name)

        messages: List[ChatMessage] = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=prompt),
        ]

        # 🔥 단 한 번만 await
        response_text = await provider.generate(messages)

        latency_ms = int((time.time() - start) * 1000)

        logger.info(
            "LLM generate success",
            extra={
                "tag": log_tag,
                "request_id": request_id,
                "latency_ms": latency_ms,
            },
        )

        return response_text