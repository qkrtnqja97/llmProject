# etl/loaders/chroma_local_loader.py

import chromadb
from chromadb.config import Settings
from config.etl_config import CHROMA_CONFIG


def get_chroma_client():
    """
    Local persistent Chroma client
    """
    client = chromadb.Client(
        Settings(
            persist_directory=CHROMA_CONFIG["persist_dir"],
            anonymized_telemetry=False
        )
    )
    return client


def get_collection(collection_name):
    client = get_chroma_client()
    return client.get_or_create_collection(name=collection_name)