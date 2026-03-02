#model_training/app/rag/chroma_client.py
"""
[RAG] Chroma Client Wrapper

📌 역할
- CHROMA_PATH 기반 persistent ChromaDB 클라이언트 생성
- 템플릿 컬렉션을 get_or_create로 확보
- index/search에서 공통으로 쓰는 연결 객체 제공

📦 사용 라이브러리
- chromadb: 벡터DB 클라이언트(템플릿 RAG)
- typing: 타입 힌트
- app.config: Settings 로딩
"""

from __future__ import annotations

from typing import Tuple

import chromadb
from chromadb.api.models.Collection import Collection

from app.config import Settings


def get_chroma_client(settings: Settings) -> chromadb.PersistentClient:
    """
    Chroma persistent client를 생성하는 함수

    Args:
        settings: 환경설정(Settings)

    Returns:
        chromadb.PersistentClient: persistent client 인스턴스
    """
    # chromadb.PersistentClient: 로컬 디스크에 인덱스 저장/로드
    return chromadb.PersistentClient(path=str(settings.chroma_path))


def get_or_create_collection(settings: Settings) -> Tuple[chromadb.PersistentClient, Collection]:
    """
    컬렉션을 생성하거나 기존 컬렉션을 가져오는 함수

    Args:
        settings: 환경설정(Settings)

    Returns:
        (client, collection): Chroma client와 collection
    """
    client = get_chroma_client(settings)

    # get_or_create_collection: 컬렉션 없으면 생성, 있으면 로드
    collection = client.get_or_create_collection(name=settings.chroma_collection)

    return client, collection