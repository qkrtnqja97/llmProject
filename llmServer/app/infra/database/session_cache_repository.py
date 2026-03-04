# llmServer/app/infra/database/session_cache_repository.py

import json
import logging
from datetime import datetime
from typing import Dict, List

from app.core.config import settings
from app.infra.database.rdb_repository import RDBRepository

logger = logging.getLogger(__name__)


class SessionCacheRepository:
    """
    세션별 대화 캐시 저장소.

    - PostgreSQL session_cache 테이블을 통해
      현재 세션의 최근 대화 목록(최대 N쌍)을 관리한다.
    - 앱 종료 시 DELETE로 초기화,
      대화 발생 시 UPSERT로 갱신한다.

    turns 포맷:
        [
            {"question": "...", "response_data": {"final_answer": "..."}},
            ...
        ]
    """

    def __init__(self, rdb_repository: RDBRepository):
        self.rdb = rdb_repository
        self.schema = settings.CONVERSATION_SCHEMA

    # --------------------------------------------------
    # 테이블 초기화 (서버 시작 시 1회 호출)
    # --------------------------------------------------
    async def ensure_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.schema}.session_cache (
            session_id TEXT PRIMARY KEY,
            user_id    TEXT        NOT NULL,
            turns      JSONB       NOT NULL DEFAULT '[]',
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        await self.rdb.execute(query)
        logger.info("[SessionCache] session_cache 테이블 준비 완료")

    # --------------------------------------------------
    # 조회
    # --------------------------------------------------
    async def get(self, session_id: str) -> List[Dict]:
        """세션 캐시의 대화 목록 반환. 없으면 빈 리스트."""
        query = f"""
        SELECT turns
        FROM {self.schema}.session_cache
        WHERE session_id = $1
        """
        row = await self.rdb.fetch_one(query, session_id)
        if not row:
            return []
        turns = row["turns"]
        # asyncpg는 JSONB를 자동 역직렬화하지만 안전하게 처리
        if isinstance(turns, str):
            turns = json.loads(turns)
        return turns if isinstance(turns, list) else []

    # --------------------------------------------------
    # 저장 (UPSERT)
    # --------------------------------------------------
    async def upsert(self, session_id: str, user_id: str, turns: List[Dict]):
        """세션 캐시 INSERT 또는 UPDATE."""
        query = f"""
        INSERT INTO {self.schema}.session_cache (session_id, user_id, turns, updated_at)
        VALUES ($1, $2, $3::jsonb, $4)
        ON CONFLICT (session_id) DO UPDATE
            SET turns      = EXCLUDED.turns,
                updated_at = EXCLUDED.updated_at
        """
        await self.rdb.execute(
            query,
            session_id,
            user_id,
            json.dumps(turns, ensure_ascii=False),
            datetime.utcnow(),
        )

    # --------------------------------------------------
    # 삭제 (세션 종료)
    # --------------------------------------------------
    async def delete(self, session_id: str):
        """세션 종료 시 캐시 삭제."""
        query = f"""
        DELETE FROM {self.schema}.session_cache
        WHERE session_id = $1
        """
        await self.rdb.execute(query, session_id)
        logger.info(f"[SessionCache] 세션 캐시 삭제: {session_id[:12]}...")
