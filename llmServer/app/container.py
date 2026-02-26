# app/container.py

from app.providers.reranker.cohere_provider import CohereRerankerProvider
from app.infra.rag.vector_repository import VectorRepository
from app.services.entity_service import EntityResolverService
from app.services.memory_service import MemoryService


class ServiceContainer:
    def __init__(self):

        # infra / provider
        self.reranker = CohereRerankerProvider()
        self.vector_repo = VectorRepository()

        # 예: DB나 캐시에서 미리 로딩
        entity_cache = {
            "manufacturers": [],
            "vendors": [],
        }

        # services
        self.entity_service = EntityResolverService(
            entity_cache=entity_cache,
            vector_repository=self.vector_repo,
            reranker=self.reranker,
        )

        self.memory_service = MemoryService()