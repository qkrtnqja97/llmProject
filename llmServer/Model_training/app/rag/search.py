#model_training/app/rag/search.py
"""
[RAG] Template Search

📌 역할
- 사용자 질문을 Chroma에 질의하여 top-k 템플릿 후보를 반환
- 반환값: pattern_id + sql_template + slots_schema + score(distance)

📦 사용 라이브러리
- typing: 타입 힌트
- app.config: Settings
- app.rag.chroma_client: collection 획득
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.config import Settings, load_settings
from app.rag.chroma_client import get_or_create_collection


def search_templates(settings: Settings, question: str) -> List[Dict[str, Any]]:
    """
    질문을 기반으로 Chroma에서 템플릿 top-k 검색

    Args:
        settings: 환경설정(Settings)
        question: 사용자 질문(자연어)

    Returns:
        list[dict]: 검색 결과 리스트
          - pattern_id
          - sql_template
          - slots_schema
          - distance (작을수록 유사)
          - example_question
    """
    if not question or not question.strip():
        return []

    _, collection = get_or_create_collection(settings)

    # collection.query: 텍스트 기반 검색(Chroma 내부 임베딩)
    result = collection.query(
        query_texts=[question],
        n_results=settings.top_k,
        include=["metadatas", "distances"],
    )

    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    outputs: List[Dict[str, Any]] = []
    for md, dist in zip(metadatas, distances):
        if not md:
            continue

        # similarity_threshold는 Chroma distance 기준(모델/설정마다 의미가 달라질 수 있음)
        # 여기서는 "0이면 필터링 안함"으로만 처리
        if settings.similarity_threshold > 0 and dist > settings.similarity_threshold:
            continue

        outputs.append(
            {
                "pattern_id": md.get("pattern_id"),
                "sql_template": md.get("sql_template"),
                "slots_schema": md.get("slots_schema"),
                "example_question": md.get("example_question"),
                "distance": dist,
            }
        )

    return outputs


if __name__ == "__main__":
    s = load_settings()
    q = "2024년 P001의 총 매출은?"
    hits = search_templates(s, q)

    print("Q:", q)
    print("Hits:", len(hits))
    for i, h in enumerate(hits, 1):
        print(f"\n[{i}] pattern_id={h['pattern_id']} dist={h['distance']}")
        print(" slots:", h["slots_schema"])
        print(" ex  :", h["example_question"])
        # sql_template은 길 수 있어서 필요할 때만 출력