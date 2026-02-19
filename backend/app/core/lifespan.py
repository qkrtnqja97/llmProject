# backend/app/core/lifespan.py
# FastAPI 애플리케이션의 수명 주기 이벤트를 관리하는 모듈입니다.

import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=10.0,
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    yield
    await app.state.http_client.aclose()
