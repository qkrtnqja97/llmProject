# llmSer
# PYTHONPATH=. python -m app.services.test.test_rerank_service

import time
from app.services.rerank_service import RerankService
from app.providers.registry import ProviderRegistry
from app.providers.reranker.cohere_provider import CohereRerankerProvider
from app.core.config import settings


def build_test_service() -> RerankService:

    if not settings.COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY가 설정되지 않았습니다.")

    registry = ProviderRegistry()

    registry.register_reranker(
        model_name="cohere-v3",
        provider=CohereRerankerProvider(
            api_key=settings.COHERE_API_KEY
        ),
    )

    reranker_provider = registry.get_reranker("cohere-v3")

    return RerankService(reranker_provider)


def run_test():

    print("🚀 RerankService 통합 테스트 시작\n")

    service = build_test_service()

    query = "network switch chip"

    docs = [
        "BCM5650 is a high-performance network switch chip",
        "Apple is a fruit",
        "Electronic components distributor company",
        "Temperature sensor IC",
    ]

    metas = [{"id": i} for i in range(len(docs))]

    start_total = time.time()

    start_call = time.time()
    final_docs, final_metas, final_scores = service.rerank(
        query=query,
        docs=docs,
        metas=metas,
        top_n=3,
        with_scores=True,
    )
    end_call = time.time()

    end_total = time.time()

    print(f"⏱ API + Rerank 처리 시간: {(end_call - start_call)*1000:.2f} ms")
    print(f"⏱ 전체 테스트 시간: {(end_total - start_total)*1000:.2f} ms\n")

    print("📊 Reranked Results:")
    for d, m, s in zip(final_docs, final_metas, final_scores):
        print(f"[{s:.4f}] - {d} | meta={m}")


if __name__ == "__main__":
    run_test()