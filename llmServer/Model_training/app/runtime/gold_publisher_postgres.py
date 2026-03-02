"""
[RUNTIME] Gold Example Publisher (PostgreSQL)

📌 역할
- sql_assistant.request_logs에서 "성공 + 만족도=1 + pattern_id 존재" 조건을 만족하는 요청을
  sql_assistant.gold_examples로 승격(publish)한다.
- 중복 승격 방지: (question, pattern_id, final_sql) 동일하면 스킵한다.

왜 필요한가?
- 운영에서 gold_examples는 "검증된 정답 데이터" 풀이다.
- 이후 템플릿 랭킹(usage_count) / sLLM 학습 / 품질 분석의 기준이 된다.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor, Json

from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def publish_gold_from_request_id(request_id: str) -> Tuple[bool, str]:
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")

            cur.execute("""
                SELECT
                  question,
                  selected_pattern_id,
                  slots_json,
                  final_sql,
                  execution_success,
                  user_satisfaction
                FROM sql_assistant.request_logs
                WHERE request_id = %s
            """, (request_id,))
            row = cur.fetchone()
            if not row:
                return (False, "request_id not found")

            if not row.get("execution_success"):
                return (False, "execution_success is false")
            if row.get("user_satisfaction") != 1:
                return (False, "user_satisfaction is not 1")
            if not row.get("selected_pattern_id"):
                return (False, "selected_pattern_id is null")
            if not row.get("final_sql"):
                return (False, "final_sql is null")

            question = row["question"]
            pattern_id = row["selected_pattern_id"]
            slots_json = row.get("slots_json") or {}
            final_sql = row["final_sql"]

            # 중복 체크
            cur.execute("""
                SELECT 1
                FROM sql_assistant.gold_examples
                WHERE question = %s
                  AND pattern_id = %s
                  AND final_sql = %s
                LIMIT 1
            """, (question, pattern_id, final_sql))
            if cur.fetchone():
                return (False, "already exists in gold_examples")

            # ✅ INSERT (커서 블록 안)
            cur.execute("""
                INSERT INTO sql_assistant.gold_examples (
                    question, pattern_id, slots_json, final_sql, created_at
                ) VALUES (
                    %s, %s, %s, %s, now()
                )
            """, (question, pattern_id, Json(_json_safe(slots_json)), final_sql))

            # ✅ gold_count +1 (커서 블록 안)
            cur.execute("""
                UPDATE sql_assistant.template_library
                SET gold_count = COALESCE(gold_count, 0) + 1,
                    updated_at = now()
                WHERE pattern_id = %s
            """, (pattern_id,))

        conn.commit()

    return (True, "published")