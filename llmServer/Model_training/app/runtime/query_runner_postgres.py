#app/runtime/query_runner_postgres.py
"""
[RUNTIME] PostgreSQL Query Runner

📌 역할
- 최종 SQL을 PostgreSQL에 실행하고 결과를 반환한다.
- SQLite 스타일 SQL(strftime 등)이 섞여 들어오는 경우 PostgreSQL 호환으로 변환한다.
- 실행 세션에 search_path(DB_SEARCH_PATH)를 적용하여 멀티 스키마 환경을 안정화한다.

왜 필요한가?
- DB가 변경되거나 스키마가 분리(inventory_mgmt / sql_assistant 등)되어도
  런타임이 동일한 search_path 기준으로 동작해야 환경 불일치 문제가 사라진다.

의존 모듈
- schema_tools.a_db_config: DB_DSN, DB_SEARCH_PATH
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import os
import re

import psycopg2
from psycopg2.extras import RealDictCursor

from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH


# [DIALECT] SQLite -> PostgreSQL 변환 규칙
RE_YEAR_SALE = re.compile(r"strftime\('%Y'\s*,\s*sale_date\)\s*=\s*(\d{4})", re.IGNORECASE)
RE_YEAR_PUR  = re.compile(r"strftime\('%Y'\s*,\s*purchase_date\)\s*=\s*(\d{4})", re.IGNORECASE)

RE_MONTH_SALE = re.compile(r"strftime\('%m'\s*,\s*sale_date\)\s*=\s*'?(\d{2})'?", re.IGNORECASE)
RE_MONTH_PUR  = re.compile(r"strftime\('%m'\s*,\s*purchase_date\)\s*=\s*'?(\d{2})'?", re.IGNORECASE)


def to_postgres_sql(sql: str) -> str:
    """
    SQLite 스타일 SQL을 PostgreSQL에서 실행 가능한 형태로 변환한다.

    Args:
        sql: SQLite 스타일 SQL (strftime 사용 등)

    Returns:
        PostgreSQL 호환 SQL
    """
    s = sql or ""

    # YEAR
    s = RE_YEAR_SALE.sub(r"EXTRACT(YEAR FROM sale_date) = \1", s)
    s = RE_YEAR_PUR.sub(r"EXTRACT(YEAR FROM purchase_date) = \1", s)

    # MONTH (01~12 -> 1~12 정수)
    def _month_sale(m: re.Match) -> str:
        return f"EXTRACT(MONTH FROM sale_date) = {int(m.group(1))}"

    def _month_pur(m: re.Match) -> str:
        return f"EXTRACT(MONTH FROM purchase_date) = {int(m.group(1))}"

    s = RE_MONTH_SALE.sub(_month_sale, s)
    s = RE_MONTH_PUR.sub(_month_pur, s)

    return s


def run_query(sql: str, row_limit: int = 200) -> Tuple[int, List[Dict[str, Any]]]:
    """
    SQL을 실행하고 결과를 (row_count, preview_rows)로 반환한다.

    Args:
        sql: 실행할 SQL
        row_limit: 최대 반환 행 수(서비스 보호)

    Returns:
        (row_count, preview_rows)
        - row_count: 반환된 행 수
        - preview_rows: 결과 일부(최대 row_limit) 리스트[dict]
    """
    preview: List[Dict[str, Any]] = []
    sql_pg = to_postgres_sql(sql)

    debug_raw = os.getenv("DEBUG", "").strip().lower()
    debug = debug_raw in ("1", "true", "yes", "y", "on")

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # ✅ 멀티 스키마 표준: DB_SEARCH_PATH 적용
            cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")

            if debug:
                cur.execute("SHOW search_path;")
                sp = cur.fetchone()
                print("[runtime] search_path =", sp)

            cur.execute(sql_pg)
            preview = cur.fetchmany(row_limit)

    return (len(preview), preview)