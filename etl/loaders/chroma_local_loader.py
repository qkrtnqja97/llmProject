# etl/loaders/chroma_local_loader.py

import chromadb
import os
from config.etl_config import CHROMA_CONFIG


def get_chroma_client():

    os.makedirs(CHROMA_CONFIG["persist_dir"], exist_ok=True)

    client = chromadb.PersistentClient(
        path=CHROMA_CONFIG["persist_dir"]
    )

    return client


def get_collection(client, collection_name):

    return client.get_or_create_collection(name=collection_name)