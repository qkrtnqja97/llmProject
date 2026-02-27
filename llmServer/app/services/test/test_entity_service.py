# test_entity_service.py
# PYTHONPATH=. python -m app.services.test.test_entity_service

from app.services.entity_service import EntityResolverService


# ---------------------------
# 1. Mock VectorRepository
# ---------------------------
class MockVectorRepository:
    def search(self, collection_name, query, top_k=3, with_distance=False):

        if collection_name == "entity":
            # part_number 유사 검색 흉내
            return [
                ("BCM5650", {"type": "part_number"}, 0.10),
                ("ABC1234", {"type": "part_number"}, 0.20),
            ]

        if collection_name == "synonym":
            return [
                ("매출액", {"canonical": "매출", "type": "metric"}),
                ("판매량", {"canonical": "판매", "type": "metric"}),
            ]

        return []


# ---------------------------
# 2. Mock RerankService
# ---------------------------
class MockRerankService:
    def rerank(self, query, docs, metas, top_n=3, with_scores=False):

        # 그냥 점수 높게 줌
        scores = [0.9 for _ in docs]

        if with_scores:
            return docs[:top_n], metas[:top_n], scores[:top_n]
        return docs[:top_n], metas[:top_n]


# ---------------------------
# 3. entity_cache 준비
# ---------------------------
entity_cache = {
    "manufacturers": ["Broadcom", "Intel"],
    "vendors": ["Digikey", "Mouser"],
}


# ---------------------------
# 4. 서비스 생성
# ---------------------------
entity_service = EntityResolverService(
    entity_cache=entity_cache,
    vector_repository=MockVectorRepository(),
    reranker=MockRerankService(),
)


# ---------------------------
# 5. 테스트 질문
# ---------------------------
question = "broadcm BCM565 매출액 알려줘"

result = entity_service.resolve(question)

print("입력 질문:", question)
print("정제 질문:", result["refined_question"])
print("동의어 힌트:", result["synonym_hint"])