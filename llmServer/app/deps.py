# llmServer/app/deps.py

from app.providers.registry import ProviderRegistry
from app.providers.llm.gemini_llm_provider import GeminiLLMProvider
from app.providers.embedding.gemini_embedding_provider import GeminiEmbeddingProvider
from app.services.llm_service import LLMService
from app.core.config import settings


# llmServer/app/deps.py

from app.providers.registry import ProviderRegistry
from app.providers.llm.gemini_llm_provider import GeminiLLMProvider
from app.providers.embedding.gemini_embedding_provider import GeminiEmbeddingProvider
from app.providers.reranker.cohere_provider import CohereRerankerProvider
from app.services.llm_service import LLMService
from app.core.config import settings

# 🔥 1️⃣ 앱 시작 시 1회 생성
registry = ProviderRegistry()

# LLM provider 등록
registry.register_llm(
    model_name="gemini-2.5-flash",
    provider=GeminiLLMProvider(
        api_key=settings.GEMINI_API_KEY,
        model_name="gemini-2.5-flash",
    ),
)

# Embedding provider 등록
registry.register_embedding(
    model_name="gemini-embedding-001",
    provider=GeminiEmbeddingProvider(
        api_key=settings.GEMINI_API_KEY,
        model_name="gemini-embedding-001",
    ),
)

# Reranker provider 등록
registry.register_reranker(
    model_name="cohere-reranker",
    provider=CohereRerankerProvider(
        api_key=settings.COHERE_API_KEY,
    ),
) 


# LLM 서비스 생성
_llm_service = LLMService(registry)

# 🔥 2️⃣ FastAPI dependency는 그냥 반환만
def get_llm_service():
    return _llm_service