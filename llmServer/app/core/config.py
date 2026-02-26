# llmServer/app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DEFAULT_SYSTEM_PROMPT: str = """
    You are a helpful AI assistant.
    Answer clearly and concisely.
    """

    COHERE_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()