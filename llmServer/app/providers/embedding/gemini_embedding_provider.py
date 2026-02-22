# llmServer/app/provider/embedding/gemini_embedding_provider.py

from google import genai
from typing import List
from app.providers.embedding.base import BaseEmbeddingProvider


class GeminiEmbeddingProvider(BaseEmbeddingProvider):

    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def embed(self, texts: List[str]) -> List[List[float]]:

        response = self.client.models.embed_content(
            model=self.model_name,
            contents=texts,
        )

        return response.embeddings