# etl/jobs/entity_embedding_job.py

import sys
import time
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from loaders.postgres_loader import connect_postgres
from loaders.chroma_loader import get_collection
from clients.gemini_embedder import GeminiEmbedder


# ============================================
# 🔹 Rate Limit 대응 (60초 / 100개)
# ============================================

def embed_with_rate_limit(embedder, documents, batch_size=100):
    all_vectors = []
    total = len(documents)

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]

        print(f"임베딩 진행: {i} ~ {i + len(batch)} / {total}")
        vectors = embedder.embed(batch)
        all_vectors.extend(vectors)

        if i + batch_size < total:
            print("⏳ 60초 대기 (Rate Limit 보호)")
            time.sleep(60)

    return all_vectors


# ============================================
# 🔹 실행
# ============================================

def run():

    print("🚀 SB_entity_store 임베딩 시작")

    engine, proc = connect_postgres()
    if engine is None:
        print("DB 연결 실패")
        return

    embedder = GeminiEmbedder()
    collection = get_collection("SB_entity_store")

    docs = []
    metas = []
    ids = []

    with engine.connect() as conn:
        conn.execute(text("SET search_path TO inventory_mgmt"))

        # ----------------------------------
        # 1️⃣ Part Number
        # ----------------------------------
        result = conn.execute(text("SELECT part_number FROM products"))
        for row in result:
            part = row[0]

            doc = f"""
품번 {part} 전자부품 part_number {part}
재고 조회 대상 제품
""".strip()

            docs.append(doc)
            metas.append({
                "type": "part_number",
                "original_id": part
            })
            ids.append(f"part_{part}")

        # ----------------------------------
        # 2️⃣ Manufacturer
        # ----------------------------------
        result = conn.execute(text("SELECT manufacturer_id, name FROM manufacturers"))
        for row in result:
            mid, name = row

            doc = f"""
제조사 공급사 납품처 {name}
manufacturer supplier
manufacturer_id {mid}
""".strip()

            docs.append(doc)
            metas.append({
                "type": "manufacturer",
                "original_id": str(mid),
                "name": name
            })
            ids.append(f"manufacturer_{mid}")

        # ----------------------------------
        # 3️⃣ Vendor
        # ----------------------------------
        result = conn.execute(text("SELECT vendor_id, vendor_name FROM vendors"))
        for row in result:
            vid, name = row

            doc = f"""
고객사 판매처 거래처 바이어 {name}
vendor client buyer
vendor_id {vid}
""".strip()

            docs.append(doc)
            metas.append({
                "type": "vendor",
                "original_id": str(vid),
                "name": name
            })
            ids.append(f"vendor_{vid}")

    print(f"총 엔티티 문서 수: {len(docs)}")

    vectors = embed_with_rate_limit(embedder, docs)

    collection.upsert(
        documents=docs,
        embeddings=vectors,
        ids=ids,
        metadatas=metas
    )

    print("✅ SB_entity_store 적재 완료")

    proc.terminate()
    print("🔒 터널 종료")


if __name__ == "__main__":
    run()