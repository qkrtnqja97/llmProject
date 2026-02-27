# llmServer/bootstrap/entity.py

from app.services.entity_service import EntityResolverService
from app.infra.rag.vector_repository import VectorRepository
from app.services.memory_service import MemoryService
from app.services.rerank_service import RerankService


def build_entity_service():

    vector_repo = VectorRepository()

    entity_cache = MemoryService()

    reranker = RerankService()

    return EntityResolverService(
        entity_cache=entity_cache,
        vector_repository=vector_repo,
        reranker=reranker,
    )
