"""
[RUNTIME] Request Logger (PostgreSQL)

- sql_assistant.request_logs(기존 스키마)에 1건 로그를 저장한다.
- 현재 DB 테이블 컬럼 스키마에 맞춰 INSERT 한다.

테이블 컬럼(현재 DB)
- request_id(uuid), user_id(varchar), question(text), refined_question(text),
  selected_pattern_id(varchar), slots_json(jsonb), entity_corrections(jsonb),
  final_sql(text), execution_success(bool), execution_time_ms(int),
  error_message(text), row_count(int), user_satisfaction(smallint), created_at(timestamptz)
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import uuid4

import psycopg2
from psycopg2.extras import Json

from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH


def _json_safe(obj: Any) -> Any:
    """
    JSON 직렬화 불가능 타입(Decimal 등)을 안전한 타입으로 변환한다.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def log_request(
    *,
    question: str,
    refined_question: Optional[str],
    selected_pattern_id: Optional[str],
    slots_json: Dict[str, Any],
    final_sql: Optional[str],
    execution_success: bool,
    execution_time_ms: Optional[int],
    row_count: Optional[int],
    error_type: Optional[str],
    error_message: Optional[str],
    user_id: Optional[str] = None,
    user_satisfaction: Optional[int] = None,
    entity_corrections: Optional[Dict[str, Any]] = None,
) -> str:
    """
    sql_assistant.request_logs에 1건 저장하고 request_id(uuid 문자열)를 반환한다.
    """
    request_id = str(uuid4())

    sql = """
        INSERT INTO sql_assistant.request_logs (
            request_id, user_id, question, refined_question,
            selected_pattern_id, slots_json, entity_corrections,
            final_sql, execution_success, execution_time_ms,
            error_message, row_count, user_satisfaction, error_type, created_at
        )
        VALUES (
            %(request_id)s, %(user_id)s, %(question)s, %(refined_question)s,
            %(selected_pattern_id)s, %(slots_json)s, %(entity_corrections)s,
            %(final_sql)s, %(execution_success)s, %(execution_time_ms)s,
            %(error_message)s, %(row_count)s, %(user_satisfaction)s, %(error_type)s,
            now()
        );
    """

    payload = {
        "request_id": request_id,
        "user_id": user_id,
        "question": question,
        "refined_question": refined_question,
        "selected_pattern_id": selected_pattern_id,
        "slots_json": Json(_json_safe(slots_json)),
        "entity_corrections": Json(_json_safe(entity_corrections or {})),
        "final_sql": final_sql,
        "execution_success": execution_success,
        "execution_time_ms": execution_time_ms,
        "error_message": error_message,
        "row_count": row_count,
        "user_satisfaction": user_satisfaction,
        "error_type": error_type,
    }

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
            cur.execute(sql, payload)
        conn.commit()

    return request_id
    
def increment_usage_count(pattern_id: Optional[str]) -> None:
    """
    template_library.usage_count를 1 증가시킨다.
    (템플릿이 선택되었을 때 호출)
    """
    if not pattern_id:
        return

    sql = """
        UPDATE sql_assistant.template_library
        SET usage_count = COALESCE(usage_count, 0) + 1,
            updated_at = now()
        WHERE pattern_id = %(pattern_id)s;
    """

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
            cur.execute(sql, {"pattern_id": pattern_id})
        conn.commit()