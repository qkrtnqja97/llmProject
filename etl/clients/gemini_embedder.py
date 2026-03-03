# etl/clients/gemini_embedder.py

from google import genai
from config.etl_config import EMBEDDING_CONFIG
from clients.base_embedder import BaseEmbedder
import time


class GeminiEmbedder(BaseEmbedder):

    def __init__(self):
        self.client = genai.Client(
            api_key=EMBEDDING_CONFIG["api_key"]
        )
        self.model = EMBEDDING_CONFIG["embedding_model"]


    def embed(self, texts: list[str], batch_size: int = 50) -> list[list[float]]:

        all_vectors = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = self.client.models.embed_content(
                model=self.model,
                contents=batch
            )

            batch_vectors = [e.values for e in response.embeddings]
            all_vectors.extend(batch_vectors)

            print(f"✅ 임베딩 배치 완료: {i} ~ {i + len(batch)}")

            #time.sleep(30)  # 무료 플랜 보호용

        return all_vectors