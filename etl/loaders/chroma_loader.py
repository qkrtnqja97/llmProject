# etl/loaders/chroma_loader.py

import chromadb
from config.etl_config import CHROMA_CONFIG


def get_chroma_client():
    """
    Cloudflare HTTPS 기반 Chroma 연결
    """
    client = chromadb.HttpClient(
        host=CHROMA_CONFIG["host"],
        port=CHROMA_CONFIG["port"],
    )
    return client


def get_collection(client,collection_name="fewshot_store"):
    return client.get_or_create_collection(name=collection_name)