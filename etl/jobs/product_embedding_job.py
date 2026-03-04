# etl/jobs/product_embedding_job.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from loaders.postgres_loader import connect_postgres
from loaders.chroma_loader import get_collection
from clients.gemini_embedder import GeminiEmbedder
from config.etl_config import POSTGRES_CONFIG
from sqlalchemy import text


def build_product_documents(engine):

    query = f"""
    SELECT 
        p.part_number,
        p.description,
        p.std_unit_cost,
        p.std_selling_price
    FROM {POSTGRES_CONFIG['schema']}.products p
    JOIN {POSTGRES_CONFIG['schema']}.current_products c
    ON p.part_number = c.part_number
    """

    documents = []
    ids = []

    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()

        for row in rows:

            doc = f"""
제품 {row.part_number}는 {row.description} 유형의 제품입니다.
이 제품의 표준 원가는 {row.std_unit_cost}이며 표준 판매가는 {row.std_selling_price}입니다.
현재 재고 관리 대상이며 재고 상태 정보가 존재합니다.

[STRUCTURED DATA]
Part Number: {row.part_number}
Description: {row.description}
Standard Cost: {row.std_unit_cost}
Standard Selling Price: {row.std_selling_price}
Inventory Managed: Yes
            """.strip()

            documents.append(doc)
            ids.append(row.part_number)

    return documents, ids


def run():
    print("🚀 Product Embedding Job 시작")

    engine,proc = connect_postgres()

    if engine is None:
        print("DB 연결 실패로 종료")
        proc.terminate()
        return

    embedder = GeminiEmbedder()
    collection = get_collection("erp_product_state_v1")

    docs, ids = build_product_documents(engine)

    print(f"총 문서 수: {len(docs)}")

    vectors = embedder.embed(docs)

    collection.upsert(
        documents=docs,
        embeddings=vectors,
        ids=ids
    )

    print("✅ 임베딩 완료")

    proc.terminate()
    print("🔒 터널 종료")


if __name__ == "__main__":
    run()