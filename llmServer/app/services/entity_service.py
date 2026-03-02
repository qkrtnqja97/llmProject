# llmServer/app/services/entity_service.py

from app.utils import text_util

# 타입 지정용
from app.services.rerank_service import RerankService
from app.infra.vector.vector_repository import VectorRepository


class EntityResolverService:
    """
    질문 안의 엔티티를 정제하는 도메인 서비스.
    - 제조사 / 판매사 fuzzy 보정
    - part_number 벡터 보정
    - 동의어 힌트 추출
    """

    ENTITY_FETCH_TOP_K = 3
    ENTITY_DISTANCE_THRESHOLD = 0.15
    FUZZY_THRESHOLD = 70
    SYNONYM_RERANK_THRESHOLD = 0.05
    SYNONYM_FETCH_TOP_K = 10

    def __init__(
        self,
        entity_cache: dict,
        vector_repository: VectorRepository,
        reranker: RerankService,
    ):
        self.entity_cache = entity_cache
        self.vector_repository = vector_repository
        self.reranker = reranker

    # =========================
    # 1. 제조사/판매사 fuzzy(문자열 유사도 비교) 보정
    # 제조사 / 판매사 데이터 받아와 유사도 검색 후 70 이상이면 이상한 이름 바꿔주기 - FUZZY_THRESHOLD
    # 1차: rapidfuzz 기반 오타 보정 (준협 주석)
    # =========================
    def _fuzzy_correct(self, question: str) -> str:
        refined = question
        names = self.entity_cache.get("manufacturers", []) + self.entity_cache.get(
            "vendors", []
        )
        # print("DEBUG names in fuzzy:", names)
        for word in question.split():
            if len(word) >= 2:
                # Utils를 사용하여 "어떻게" 하는지 감춤
                matched_name = text_util.get_fuzzy_match(
                    word, names, self.FUZZY_THRESHOLD
                )
                if matched_name:
                    refined = refined.replace(word, matched_name)
        return refined

    # =========================
    # 2. part_number 벡터 보정
    # 1 관문 : 벡터 디비에서 유사도 검색
    # 2 관문 : 1관문 통과되면 문자열 비교
    # 2차: entity_store 벡터 검색으로 part_number 오타 보정 (준협 주석)
    # =========================
    async def _vector_correct_part_number(self, question: str) -> str:
        refined = question

        # 파트넘버 벡터 유사도 비교 (top_k 설정 가능. default:3)
        candidates = await self.vector_repository.search_by_text(
            collection_name="SB_entity_store",
            query_text=question,
            top_k=self.ENTITY_FETCH_TOP_K,
        )
        # print("DEBUG candidates in part_num:", candidates)
        
        for doc, meta, dist in candidates:
            # 1관문: 벡터 거리 체크
            if (
                dist < self.ENTITY_DISTANCE_THRESHOLD
                and meta.get("type") == "part_number"
            ):
                # 2관문: 벡터 공간에서 비교했다면 -> 문자열로 세부 비교 (Utils 호출)
                candidate_part = meta.get("original_id")
                for word in question.split():
                    if text_util.is_valid_part_number_match(word, candidate_part, threshold=0.8):
                        if word.upper() != doc.upper():
                            refined = refined.replace(word, candidate_part)

        return refined

    # =========================
    # 3. 동의어 검색 (벡터 + 리랭킹)
    #
    # 후보 10개 → 리랭킹 → 상위 n개 중 점수 임계값 통과분 반환
    # =========================
    async def _retrieve_synonyms(self, question: str, top_n: int = 3) -> str:

        # 후보 10개 조회
        candidates = await self.vector_repository.search_by_text(
            collection_name="SB_synonym_store",
            query_text=question,
            top_k=10,
        )
        # print("DEBUG candidates in synonyms:", candidates)
        if not candidates:
            return ""

        cand_docs = [doc for doc, _, _ in candidates]
        cand_metas = [meta for _, meta, _ in candidates]

        # 리랭킹 + 점수
        final_docs, final_metas, final_scores = await self.reranker.rerank(
            question, cand_docs, cand_metas, top_n=top_n, with_scores=True
        )

        hints = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            # 디버깅용 프린트문
            # print("DEBUG:", doc, score)
            # print("DEBUG synonym 후보 수:", len(cand_docs))
            # print("DEBUG rerank score:", doc, score)
            if score > self.SYNONYM_RERANK_THRESHOLD:  # 리랭커 정규화 점수 임계값
                hints.append(
                    f"'{doc}' → '{meta.get('canonical')}' ({meta.get('type')})"
                )

        return ", ".join(hints) if hints else ""

    # 아직 메모리 기능은 안넣음
    # def _inject_memory(self, question: str, memory: dict) -> str:
    #     if not memory:
    #         return question

    #     q = question

    #     PRONOUN_MAP = {
    #         "이 제품": "last_product",
    #         "해당 제품": "last_product",
    #         "그 제품": "last_product",
    #         "이 고객사": "last_vendor",
    #         "해당 고객사": "last_vendor",
    #         "이 제조사": "last_manufacturer",
    #         "해당 제조사": "last_manufacturer",
    #     }

    #     for pronoun, key in PRONOUN_MAP.items():
    #         if pronoun in q and memory.get(key):
    #             q = q.replace(pronoun, f"'{memory[key]}'")

    #     if "같은 기간" in q and memory.get("last_date_range"):
    #         q += f" (기간조건: {memory['last_date_range']})"

    #     return q

    # =========================
    # 외부 호출용 API
    # =========================
    async def resolve(self, question: str) -> dict:
        refined = self._fuzzy_correct(question)
        refined = await self._vector_correct_part_number(refined)
        synonym_hint = await self._retrieve_synonyms(question)
        # 아직 메모리 기능은 안넣음 -> 메모리 서비스로 따로 빼기.
        # refined = self._inject_memory(refined, memory)

        return {
            "refined_question": refined,
            "synonym_hint": synonym_hint,
        }
