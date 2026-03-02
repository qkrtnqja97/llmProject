# llmServer/app/services/test/test_embedding_service.py
# PYTHONPATH=. python -m app.services.test.test_embedding_service

import time
import asyncio

from app.core.logging.logging_config import setup_logging
from app.core.logging.request_context import generate_request_id, set_request_id

from app.providers.registry import ProviderRegistry
from app.providers.embedding.gemini_embedding_provider import GeminiEmbeddingProvider
from app.services.embedding_service import EmbeddingService
from app.core.config import settings


async def main():

    setup_logging()

    request_id = generate_request_id()
    set_request_id(request_id)

    print("\n🚀 EmbeddingService 통합 테스트 시작")
    print("request_id:", request_id, "\n")

    registry = ProviderRegistry()

    embedding_provider = GeminiEmbeddingProvider(
        api_key=settings.GEMINI_API_KEY,
        model_name=settings.EMBEDDING_MODEL,
    )

    registry.register_embedding(settings.EMBEDDING_MODEL, embedding_provider)

    embedding_service = EmbeddingService(
        embedding_provider=registry.get_embedding(settings.EMBEDDING_MODEL)
    )

    texts = [
        "network switch chip",
        "temperature sensor",
    ]

    start = time.time()

    vectors = await embedding_service.embed(texts)

    latency = (time.time() - start) * 1000

    print(f"\n⏱ Embedding 처리 시간: {latency:.2f} ms")
    print("Vector count:", len(vectors))
    print("Vector dimension:", len(vectors[0]) if vectors else 0)


if __name__ == "__main__":
    asyncio.run(main())