# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 환경변수(.env)에서 읽어올 필드들 정의
    LLM_SERVER_URL: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1200

    # .env 파일을 찾아서 로드하는 설정
    # env_file_encoding은 한글 주석 등이 있을 수 있어 utf-8로 권장합니다.
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # .env에 정의되지 않은 다른 변수가 있어도 무시
    )

settings = Settings()