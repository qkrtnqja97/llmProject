# llmServer/etl/jobs/sqlgen_embedding_job_sb.py
# python -m jobs.sqlgen_embedding_job_sb

from loaders.chroma_local_loader import get_collection, get_chroma_client
from clients.gemini_embedder import GeminiEmbedder
from jobs.static_data import TABLE_SCHEMA_DATA, BIZTERM_DATA, FEWSHOT_EXAMPLES


RESET = False

embedder = GeminiEmbedder()
client = get_chroma_client()


# -------------------------------------------------
# SB SCHEMA
# -------------------------------------------------

def load_schema():

    print("\n🚀 SB Schema")

    collection = get_collection(client,"SB_table_schema_store")

    if RESET:
        collection.delete(where={})

    docs = []
    ids = []
    metas = []

    for schema in TABLE_SCHEMA_DATA:

        doc = f"""
Table: {schema['id']}

Columns:
{schema['metadatas']['columns']}

Description:
{schema['description']}

Rules:
{schema['metadatas']['sql']}
""".strip()

        docs.append(doc)
        ids.append(schema["id"])
        metas.append(schema["metadatas"])

    vectors = embedder.embed(docs)

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=vectors,
        metadatas=metas
    )

    print(f"✅ {len(ids)} SB schema 적재")


# -------------------------------------------------
# SB BIZTERM
# -------------------------------------------------

def load_bizterm():

    print("\n🚀 SB BizTerm")

    collection = get_collection(client,"SB_bizterm_store")

    if RESET:
        collection.delete(where={})

    docs = []
    ids = []
    metas = []

    for term in BIZTERM_DATA:

        doc = f"""
Business Term: {term['description']}

Definition:
{term['metadatas']['sql']}
""".strip()

        docs.append(doc)
        ids.append(term["id"])
        metas.append(term["metadatas"])

    vectors = embedder.embed(docs)

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=vectors,
        metadatas=metas
    )

    print(f"✅ {len(ids)} SB bizterm 적재")


# -------------------------------------------------
# SB FEWSHOT
# -------------------------------------------------

def load_fewshot():

    print("\n🚀 SB Fewshot")

    collection = get_collection(client,"SB_fewshot_store")

    if RESET:
        collection.delete(where={})

    docs = []
    ids = []
    metas = []

    for i, item in enumerate(FEWSHOT_EXAMPLES):

        doc = f"""
SQL Example

Question:
{item['q']}

SQL:
{item['sql']}
""".strip()

        docs.append(doc)
        ids.append(f"fewshot_{i}")

        metas.append({
            "type": "fewshot_sql",
            "sql": item["sql"]
        })

    vectors = embedder.embed(docs)

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=vectors,
        metadatas=metas
    )

    print(f"✅ {len(ids)} SB fewshot 적재")


def run():

    print("🔥 SB Embedding Start")

    load_schema()
    load_bizterm()
    load_fewshot()

    print("\n🎉 SB 완료")


if __name__ == "__main__":
    run()