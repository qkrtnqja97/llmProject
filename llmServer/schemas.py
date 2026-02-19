# llmServer/schemas.py
# LLM 서버와 통신하기 위한 Pydantic 모델 정의

from pydantic_settings import BaseSettings

class GenerateRequest(BaseSettings):
    prompt: str

class GenerateResponse(BaseSettings):
    text: str
