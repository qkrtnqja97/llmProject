# backend/app/core/config.py
# 애플리케이션의 설정을 관리하는 모듈입니다.

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_SERVER_URL: str = "http://llm:9000"

settings = Settings()