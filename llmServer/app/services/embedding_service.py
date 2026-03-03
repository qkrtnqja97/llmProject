# llmServer/app/services/embedding_service.py

import logging
from typing import List

from app.providers.embedding.base import BaseEmbeddingProvider
from app.core.logging.logging_tags import LogTag
from app.core.logging.request_context import get_request_id

logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider

    async def embed(self, texts: List[str]) -> List[List[float]]:

        request_id = get_request_id()

        logger.info(
            "Embedding start",
            extra={
                "tag": LogTag.REQUEST,
                "request_id": request_id,
                "text_count": len(texts),
            },
        )

        try:
            vectors = await self.embedding_provider.embed(texts)

        except Exception as e:
            logger.exception(
                "Embedding failed",
                extra={
                    "tag": LogTag.REQUEST,
                    "request_id": request_id,
                },
            )
            raise RuntimeError("Embedding failed") from e

        logger.info(
            "Embedding success",
            extra={
                "tag": LogTag.REQUEST,
                "request_id": request_id,
                "vector_count": len(vectors),
            },
        )

        return vectors