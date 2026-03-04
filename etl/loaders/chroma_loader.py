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
        ssl=CHROMA_CONFIG["ssl"]
    )
    return client


def get_collection(collection_name="erp_collection"):
    client = get_chroma_client()
    return client.get_or_create_collection(name=collection_name)