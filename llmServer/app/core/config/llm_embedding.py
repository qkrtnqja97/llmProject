# llmServer/app/core/config/llm.py

from app.core.config.base import BaseAppSettings


class LLM_EMBEDDING_Settings(BaseAppSettings):
    GEMINI_API_KEY: str
    LLM_MODEL: str
    EMBEDDING_MODEL: str

    router_model: str = "gemini-2.5-flash"
    sql_model: str = "gemini-2.5-flash"
    answer_model: str = "gemini-2.5-flash"
    chitchat_model: str = "gemini-2.5-flash"
    
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_LLM_DEPLOYMENT_NAME: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str
    