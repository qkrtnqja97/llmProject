# backend/app/core/lifespan.py
# FastAPI 애플리케이션의 수명 주기 이벤트를 관리하는 모듈입니다.

import httpx
import asyncpg
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. HTTP Client 초기화
    app.state.http_client = httpx.AsyncClient(
        timeout=10.0,
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    
    # 2. DB Connection Pool 초기화 (예외 처리 추가)
    try:
        app.state.db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60.0
        )
        logger.info("✅ Database connection pool created successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to create database pool: {e}")
        raise e # DB 없이는 서비스 불가능하므로 중단
    
    yield
    
    # 3. 자원 해제
    await app.state.http_client.aclose()
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.close()
        logger.info("✅ Database connection pool closed.")