# etl/jobs/test/test_product_embedding.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from clients.embedder_factory import get_embedder
from loaders.chroma_loader import get_collection

if __name__ == "__main__":

    print("🔎 벡터 검색 테스트 시작")

    embedder = get_embedder()
    collection = get_collection("erp_product_state_v1")

    print("📦 현재 문서 수:", collection.count())

    queries = [
        "IC 제품 재고 상태 알려줘",
        "ELJRF47NJFB 원가 얼마야?",
        "이 제품 판매가 얼마야?",
        "재고 있는 제품 보여줘"
    ]

    for q in queries:
        print("\n==============================")
        print("🧠 질문:", q)

        query_vector = embedder.embed([q])[0]

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=1
        )

        docs = results["documents"][0]

        for i, doc in enumerate(docs):
            print(f"\n--- Top {i+1} ---")
            print(doc[:300])