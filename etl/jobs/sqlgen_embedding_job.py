# etl/jobs/sqlgen_embedding_job.py
# python jobs/sqlgen_embedding_job.py

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from loaders.chroma_local_loader import get_collection
from clients.gemini_embedder import GeminiEmbedder

from static_data import (
    FEWSHOT_EXAMPLES,
    BIZTERM_DATA,
    TABLE_SCHEMA_DATA,
)

# ============================================
# 🔹 Rate Limit 대응 (Gemini)
# ============================================

def embed_with_rate_limit(embedder, documents, batch_size=100):

    all_vectors = []
    total = len(documents)

    for i in range(0, total, batch_size):

        batch = documents[i:i + batch_size]

        print(f"임베딩 진행중: {i} ~ {i + len(batch)} / {total}")

        vectors = embedder.embed(batch)
        all_vectors.extend(vectors)

        # 무료버전이면 필요 없음
        # if i + batch_size < total:
        #     print("⏳ 60초 대기")
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

    print("🔥 SQLGen Embedding Job 시작")

    # -------------------------------------------------
    # 1️⃣ TABLE SCHEMA STORE
    # -------------------------------------------------

    schema_docs = [item["doc"] for item in TABLE_SCHEMA_DATA]
    schema_ids = [f"schema_{i}" for i in range(len(TABLE_SCHEMA_DATA))]
    schema_meta = [item["meta"] for item in TABLE_SCHEMA_DATA]

    process_collection(
        "SB_schema_store",
        schema_docs,
        schema_ids,
        schema_meta
    )


    # -------------------------------------------------
    # 2️⃣ BIZTERM STORE
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
        biz_meta.append({
            "type": "bizterm"
        })

    process_collection(
        "SB_bizterm_store",
        biz_docs,
        biz_ids,
        biz_meta
    )


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
        fewshot_meta.append({
            "type": "fewshot_sql"
        })

    process_collection(
        "SB_fewshot_store",
        fewshot_docs,
        fewshot_ids,
        fewshot_meta
    )

    print("\n🎉 SQLGen 컬렉션 적재 완료")


# ============================================

if __name__ == "__main__":
    run()