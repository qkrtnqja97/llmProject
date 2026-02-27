# llmServer/app/core/config.py

from pydantic_settings import BaseSettings
from app.prompts.router_prompt import BASE_ROUTER_SYSTEM_PROMPT


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DEFAULT_SYSTEM_PROMPT: str = """
    You are a helpful AI assistant.
    Answer clearly and concisely.
    """

    COHERE_API_KEY: str

    class Config:
        env_file = ".env"

    ROUTER_SYSTEM_PROMPT: str = BASE_ROUTER_SYSTEM_PROMPT


settings = Settings()
