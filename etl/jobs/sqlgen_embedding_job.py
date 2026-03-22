# etl/jobs/sqlgen_embedding_job.py
# python -m jobs.sqlgen_embedding_job

from loaders.chroma_loader import get_collection, get_chroma_client
from clients.gemini_embedder import GeminiEmbedder
from jobs.static_data import TABLE_SCHEMA_DATA, BIZTERM_DATA, FEWSHOT_EXAMPLES


RESET = False

embedder = GeminiEmbedder()
client = get_chroma_client()


# -------------------------------------------------
# Table Schema
# -------------------------------------------------

def load_schema():

    print("\n🚀 BASELINE Schema")

    collection = get_collection(client, "table_schema_store")

    if RESET:
        collection.delete(where={})

    docs = []
    ids = []
    metas = []

    for schema in TABLE_SCHEMA_DATA:

        docs.append(schema["description"])
        ids.append(schema["id"])
        metas.append(schema["metadatas"])

    vectors = embedder.embed(docs)

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=vectors,
        metadatas=metas
    )

    print(f"✅ {len(ids)} schema 적재")


# -------------------------------------------------
# BIZTERM
# -------------------------------------------------

def load_bizterm():

    print("\n🚀 BASELINE BizTerm")

    collection = get_collection(client, "bizterm_store")

    if RESET:
        collection.delete(where={})

    docs = []
    ids = []
    metas = []

    for term in BIZTERM_DATA:

        docs.append(term["description"])
        ids.append(term["id"])
        metas.append(term["metadatas"])

    vectors = embedder.embed(docs)

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=vectors,
        metadatas=metas
    )

    print(f"✅ {len(ids)} bizterm 적재")


# -------------------------------------------------
# FEWSHOT
# -------------------------------------------------

def load_fewshot():

    print("\n🚀 BASELINE Fewshot")

    collection = get_collection(client, "fewshot_store")

    if RESET:
        collection.delete(where={})

    docs = []
    ids = []
    metas = []

    for i, item in enumerate(FEWSHOT_EXAMPLES):

        doc = f"""
[QUESTION]
{item['q']}

[SQL]
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

    print(f"✅ {len(ids)} fewshot 적재")


def run():

    print("🔥 BASELINE Embedding Start")

    load_schema()
    load_bizterm()
    load_fewshot()


    print("\n🎉 BASELINE 완료")


if __name__ == "__main__":
    run()