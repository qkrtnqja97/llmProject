# app/container.py

from app.prompts.registry import PromptRegistry
from app.providers.registry import ProviderRegistry
from app.infra.vector.vector_repository import VectorRepository
from app.infra.database.conversation_repository import ConversationRepository

from app.services.entity_service import EntityResolverService
from app.services.router_service import RouterService
from app.services.memory_service import MemoryService
from app.services.llm_service import LLMService
from app.services.rerank_service import RerankService
from app.services.rag_service import RAGService
from app.services.memory_service import MemoryService
from app.services.retrieval.engine import RetrievalEngine
from app.services.retrieval.bm25 import BM25Index
from app.services.retrieval.fewshot_manager import FewshotManager

from app.core.config import settings
from app.core.metadata_bundle import MetadataBundle

class ServiceContainer:

    def __init__(
        self,
        *,
        prompt_registry: PromptRegistry,
        provider_registry: ProviderRegistry,
        vector_repository: VectorRepository,
        conversation_repository: ConversationRepository,
        metadata_bundle: MetadataBundle,
    ):
        # 🔹 Provider 기반 객체 생성
        _reranker_provider = provider_registry.get_reranker(settings.COHERE_MODEL)
        self.conversation_repository = conversation_repository

        # 🔹 Application Services
        self.llm_service = LLMService(
            llm_registry=provider_registry,
            prompt_registry=prompt_registry,
        )

        self.rerank_service = RerankService(
            reranker=_reranker_provider
        )

        self.router_service = RouterService(
            llm_service=self.llm_service
        )

        self.memory_service = MemoryService(conversation_repository=conversation_repository)

        self.entity_service = EntityResolverService(
            entity_cache=metadata_bundle.entity_cache,
            vector_repository=vector_repository,
            reranker=self.rerank_service,
        )
        
        
        
        
         # ─────────────────────────────
        # 🔥 RAG Stack
        # ─────────────────────────────

        # 1️⃣ BM25 (fewshot용)
        self.bm25_index = BM25Index(
            vector_repository=vector_repository,
            collection_name="fewshot",
        )

        # 2️⃣ Retrieval Engine
        self.retrieval_engine = RetrievalEngine(
            vector_repository=vector_repository,
            rerank_service=self.rerank_service,
            bm25_index=self.bm25_index,
        )

        # 3️⃣ RAG Service
        self.rag_service = RAGService(
            retrieval_engine=self.retrieval_engine
        )

        # 4️⃣ Fewshot Self-Learning
        self.fewshot_manager = FewshotManager(
            vector_repository=vector_repository,
            bm25_index=self.bm25_index,
        )