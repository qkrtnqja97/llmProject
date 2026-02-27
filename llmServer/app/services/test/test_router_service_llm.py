# PYTHONPATH=. python -m app.services.test.test_router_service_llm

import time
import asyncio

from app.services.router_service import RouterService
from app.services.llm_service import LLMService
from app.providers.registry import ProviderRegistry
from app.prompts.registry import PromptRegistry
from app.providers.llm.gemini_llm_provider import GeminiLLMProvider
from app.core.config import settings


def build_router():

    registry = ProviderRegistry()
    prompt_registry = PromptRegistry()

    # ✅ 올바른 등록 함수
    registry.register_llm(
        model_name="gemini-2.5-flash",
        provider=GeminiLLMProvider(
            api_key=settings.GEMINI_API_KEY,
            model_name="gemini-2.5-flash",
        ),
    )

    llm_service = LLMService(registry=registry, prompt_registry=prompt_registry)

    return RouterService(llm_service)


async def run_test():

    print("🚀 RouterService LLM fallback 테스트\n")

    router = build_router()

    question = "이거 좀 설명해줘"

    start = time.time()
    intent = await router.route(question)
    end = time.time()

    print("질문:", question)
    print("분류:", intent)
    print(f"⏱ 처리 시간: {(end-start)*1000:.2f} ms")


if __name__ == "__main__":
    asyncio.run(run_test())
