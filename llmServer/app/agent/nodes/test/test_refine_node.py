# llmServer/app/agent/nodes/test/test_refine_node.py

# PYTHONPATH=. python -m app.agent.test.test_refine_node

import time

from app.agent.nodes.refine_node import RefineNode
from app.services.entity_service import EntityResolverService
from app.services.rerank_service import RerankService
from app.providers.registry import ProviderRegistry
from app.providers.reranker.cohere_provider import CohereRerankerProvider
from app.core.config import settings


# ---------------------------
# Mock VectorRepository (Chroma 대신)
# ---------------------------
class MockVectorRepository:
    def search(self, collection_name, query, top_k=3, with_distance=False):

        if collection_name == "entity":
            return [
                ("BCM5650", {"type": "part_number"}, 0.10),
            ]

        if collection_name == "synonym":
            return [
                ("매출액", {"canonical": "매출", "type": "metric"}),
                ("판매량", {"canonical": "판매", "type": "metric"}),
                ("총매출", {"canonical": "매출", "type": "metric"}),
                ("수익", {"canonical": "매출", "type": "metric"}),
            ]

        return []


# ---------------------------
# Mock MemoryService
# ---------------------------
class MockMemoryService:
    def inject(self, question, memory):
        return question


def build_refine_node():

    if not settings.COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY가 설정되지 않았습니다.")

    # 1️⃣ Registry 구성
    registry = ProviderRegistry()

    registry.register_reranker(
        model_name="cohere-v3",
        provider=CohereRerankerProvider(api_key=settings.COHERE_API_KEY),
    )

    reranker_provider = registry.get_reranker("cohere-v3")

    # 2️⃣ 서비스 구성
    rerank_service = RerankService(reranker_provider)

    entity_cache = {
        "manufacturers": ["Broadcom", "Intel"],
        "vendors": ["Digikey", "Mouser"],
    }

    entity_service = EntityResolverService(
        entity_cache=entity_cache,
        vector_repository=MockVectorRepository(),
        reranker=rerank_service,
    )

    memory_service = MockMemoryService()

    return RefineNode(
        entity_service=entity_service,
        memory_service=memory_service,
    )


def run_test():

    print("🚀 RefineNode + Cohere 통합 테스트 시작\n")

    refine_node = build_refine_node()

    state = {
        "question": "broadcm BCM565 매출액 알려줘",
        "structured_memory": {},
    }

    start = time.time()

    result = refine_node(state)

    end = time.time()

    print(f"⏱ RefineNode 전체 처리 시간: {(end - start)*1000:.2f} ms\n")

    print("📌 결과:")
    print("refined_question:", result["refined_question"])
    print("synonym_hint:", result["synonym_hint"])


if __name__ == "__main__":
    run_test()
