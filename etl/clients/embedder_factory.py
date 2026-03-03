# etl/clients/embedder_factory.py

from config.etl_config import EMBEDDING_CONFIG
from clients.gemini_embedder import GeminiEmbedder


def get_embedder():

    provider = EMBEDDING_CONFIG.get("provider", "gemini")

    if provider == "gemini":
        return GeminiEmbedder()

    # 나중에 추가
    # elif provider == "voyage":
    #     return VoyageEmbedder()

    else:
        raise ValueError(f"지원하지 않는 임베딩 provider: {provider}")