# app/infra/vector/chroma_factory.py

import chromadb
from chromadb.utils import embedding_functions

from app.infra.rag.vector_repository import VectorRepository


def build_chroma_repository(
    persist_path: str,
    embedding_model: str,
) -> VectorRepository:

    # 1. client 생성
    client = chromadb.PersistentClient(path=persist_path)

    # 2. embedding 함수
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )

    # 3. 필요한 컬렉션들 로드 or 생성
    def safe_get(name: str):
        try:
            return client.get_collection(
                name=name,
                embedding_function=embedding_fn,
            )
        except Exception:
            # 없으면 생성
            return client.get_or_create_collection(
                name=name,
                embedding_function=embedding_fn,
            )

    collections = {
        "fewshot": safe_get("fewshot_sql"),
        "synonym": safe_get("synonym_store"),
        "entity": safe_get("entity_store"),
        "schema": safe_get("table_schema"),
        "error": safe_get("error_pattern"),
        "keyword": safe_get("keyword_intent"),
    }

    return VectorRepository(collections)
