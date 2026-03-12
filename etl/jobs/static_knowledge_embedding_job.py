# etl/jobs/static_knowledge_embedding_job.py

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from loaders.chroma_loader import get_collection
from clients.gemini_embedder import GeminiEmbedder

from static_data import (
    FEWSHOT_EXAMPLES,
    SYNONYM_DATA,
    BIZTERM_DATA,
    TABLE_SCHEMA_DATA,
    ERROR_PATTERN_DATA,
    KEYWORD_INTENT_DATA,
)

# ============================================
# 🔹 Rate Limit 대응 (60초 / 100개)
# ============================================

def embed_with_rate_limit(embedder, documents, batch_size=100):
    all_vectors = []
    total = len(documents)

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]

        print(f"임베딩 진행중: {i} ~ {i + len(batch)} / {total}")

        vectors = embedder.embed(batch)
        all_vectors.extend(vectors)
        
        # 유료버전
        # if i + batch_size < total:
        #     print("⏳ 60초 대기 (Rate Limit 보호)")
        #     time.sleep(60)

    return all_vectors


# ============================================
# 🔹 공통 업서트 함수
# ============================================

def process_collection(name, documents, ids, metadatas):
    print(f"\n🚀 {name} 적재 시작")
    print(f"총 문서 수: {len(documents)}")

    embedder = GeminiEmbedder()
    collection = get_collection(name)

    vectors = embed_with_rate_limit(embedder, documents)

    collection.upsert(
        documents=documents,
        embeddings=vectors,
        ids=ids,
        metadatas=metadatas
    )

    print(f"✅ {name} 적재 완료")


# ============================================
# 🔹 실행
# ============================================

def run():

    print("🔥 Static Knowledge Multi-Collection Embedding Job 시작")

    # -------------------------------------------------
    # 1️⃣ SCHEMA STORE
    # -------------------------------------------------
    schema_docs = [item["doc"] for item in TABLE_SCHEMA_DATA]
    schema_ids = [f"schema_{i}" for i in range(len(TABLE_SCHEMA_DATA))]
    schema_meta = [item["meta"] for item in TABLE_SCHEMA_DATA]

    process_collection("SB_schema_store", schema_docs, schema_ids, schema_meta)

    # -------------------------------------------------
    # 2️⃣ ERROR STORE
    # -------------------------------------------------
    error_docs = [item["doc"] for item in ERROR_PATTERN_DATA]
    error_ids = [f"error_{i}" for i in range(len(ERROR_PATTERN_DATA))]
    error_meta = [item["meta"] for item in ERROR_PATTERN_DATA]

    process_collection("SB_error_store", error_docs, error_ids, error_meta)

    # -------------------------------------------------
    # 3️⃣ FEWSHOT STORE
    # -------------------------------------------------
    fewshot_docs = []
    fewshot_ids = []
    fewshot_meta = []

    for i, item in enumerate(FEWSHOT_EXAMPLES):
        doc = f"""
[QUESTION]
{item['q']}

[SQL]
{item['sql']}
""".strip()

        fewshot_docs.append(doc)
        fewshot_ids.append(f"fewshot_{i}")
        fewshot_meta.append({"type": "fewshot_sql"})

    process_collection("SB_fewshot_store", fewshot_docs, fewshot_ids, fewshot_meta)

    # -------------------------------------------------
    # 4️⃣ SYNONYM STORE
    # -------------------------------------------------
    synonym_docs = []
    synonym_ids = []
    synonym_meta = []

    for i, item in enumerate(SYNONYM_DATA):
        doc = f"""
동의어: {item['term']}
정식명: {item['canonical']}
타입: {item['type']}
""".strip()

        synonym_docs.append(doc)
        synonym_ids.append(f"synonym_{i}")
        synonym_meta.append({"type": "synonym", "refine_type": item["type"]})

    process_collection("SB_synonym_store", synonym_docs, synonym_ids, synonym_meta)

    # -------------------------------------------------
    # 5️⃣ BIZTERM STORE
    # -------------------------------------------------
    biz_docs = []
    biz_ids = []
    biz_meta = []

    for i, item in enumerate(BIZTERM_DATA):
        doc = f"""
비즈니스 용어: {item['term']}

설명:
{item['desc']}
""".strip()

        biz_docs.append(doc)
        biz_ids.append(f"biz_{i}")
        biz_meta.append({"type": "bizterm"})

    process_collection("SB_bizterm_store", biz_docs, biz_ids, biz_meta)

    # -------------------------------------------------
    # 6️⃣ INTENT STORE
    # -------------------------------------------------
    intent_docs = [item["doc"] for item in KEYWORD_INTENT_DATA]
    intent_ids = [f"intent_{i}" for i in range(len(KEYWORD_INTENT_DATA))]
    intent_meta = [item["meta"] for item in KEYWORD_INTENT_DATA]

    process_collection("SB_intent_store", intent_docs, intent_ids, intent_meta)

    print("\n🎉 모든 컬렉션 적재 완료")


if __name__ == "__main__":
    run()