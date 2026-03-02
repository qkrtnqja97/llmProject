#b_schema_snapshot.py
"""
[SCHEMA_SNAPSHOT] LLM/RAG 입력용 스키마 스냅샷 생성기

역할:
- 지정한 스키마의 테이블 구조를 "LLM 입력용 schema_snapshot" 포맷으로 생성
- 테이블별 컬럼 목록 + PK + FK 포함
- (옵션) 여러 스키마/전체 스키마 덤프 가능
- 결과를 txt + json으로 저장하여 RAG/프롬프트에 그대로 사용

출력:
- train_data/schema_snapshot/schema_snapshot.txt
- train_data/schema_snapshot/schema_snapshot.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

import psycopg2

from schema_tools.a_db_config import DB_DSN, DB_SCHEMA


# -----------------------------
# 경로(프로젝트 루트 기준)
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]  # .../schema_tools/.. => project root
OUTPUT_DIR = ROOT / "train_data" / "schema_snapshot"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_TXT = OUTPUT_DIR / "schema_snapshot.txt"
OUTPUT_JSON = OUTPUT_DIR / "schema_snapshot.json"

# 특정 테이블만 LLM에 제공하고 싶으면 여기에 넣으면 됨(화이트리스트).
TABLE_WHITELIST: List[str] = []


def _list_schemas(conn) -> List[str]:
    """
    시스템 스키마 제외한 사용자 스키마 목록을 반환
    """
    q = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
          AND schema_name NOT LIKE 'pg_toast%'
          AND schema_name NOT LIKE 'pg_temp_%'
        ORDER BY schema_name;
    """
    with conn.cursor() as cur:
        cur.execute(q)
        return [r[0] for r in cur.fetchall()]


def _fetch_schema_rows(conn, target_schema: str) -> Tuple[List[Tuple], List[Tuple], List[Tuple]]:
    """
    특정 스키마에 대해 cols/pk/fk raw rows를 조회

    Returns:
        (cols_rows, pk_rows, fk_rows)
    """
    cols_query = """
        SELECT table_name, column_name, data_type, ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
    """

    pk_query = """
        SELECT kcu.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = %s
        ORDER BY kcu.table_name, kcu.ordinal_position;
    """

    fk_query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_schema_name,
            ccu.table_name  AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = %s
        ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position;
    """

    with conn.cursor() as cur:
        cur.execute(cols_query, (target_schema,))
        cols_rows = cur.fetchall()

        cur.execute(pk_query, (target_schema,))
        pk_rows = cur.fetchall()

        cur.execute(fk_query, (target_schema,))
        fk_rows = cur.fetchall()

    return cols_rows, pk_rows, fk_rows


def _build_snapshot_for_schema(cols_rows, pk_rows, fk_rows, target_schema: str) -> Dict[str, Any]:
    """
    raw rows -> 구조화 snapshot(dict)
    """
    schema_cols: Dict[str, List[Tuple[str, str]]] = {}
    for table, col, dtype, _pos in cols_rows:
        if TABLE_WHITELIST and table not in TABLE_WHITELIST:
            continue
        schema_cols.setdefault(table, []).append((col, dtype))

    pk_map: Dict[str, set[str]] = {}
    for table, col in pk_rows:
        if TABLE_WHITELIST and table not in TABLE_WHITELIST:
            continue
        pk_map.setdefault(table, set()).add(col)

    fk_lines: List[str] = []
    for table, col, f_schema, f_table, f_col in fk_rows:
        if TABLE_WHITELIST and (table not in TABLE_WHITELIST or f_table not in TABLE_WHITELIST):
            continue
        fk_lines.append(f"{table}.{col} -> {f_schema}.{f_table}.{f_col}")

    tables_obj = []
    for table in sorted(schema_cols.keys()):
        cols = []
        pk_set = pk_map.get(table, set())
        for col, dtype in schema_cols[table]:
            cols.append(
                {
                    "name": col,
                    "data_type": dtype,
                    "is_pk": col in pk_set,
                }
            )
        tables_obj.append({"table": table, "columns": cols})

    return {
        "schema": target_schema,
        "tables": tables_obj,
        "foreign_keys": sorted(set(fk_lines)),
    }


def _render_text(snapshot_all: Dict[str, Any]) -> str:
    """
    LLM/RAG 입력용 텍스트 렌더링
    """
    lines: List[str] = []
    lines.append("# schema_snapshot")
    lines.append("")

    for sch in snapshot_all["schemas"]:
        lines.append(f"## schema: {sch['schema']}")
        lines.append("tables:")
        for t in sch["tables"]:
            cols_txt = []
            for c in t["columns"]:
                name = c["name"]
                if c["is_pk"]:
                    name = f"{name} PK"
                cols_txt.append(name)
            lines.append(f"- {t['table']}({', '.join(cols_txt)})")

        lines.append("FK:")
        if sch["foreign_keys"]:
            for fk in sch["foreign_keys"]:
                lines.append(f"- {fk}")
        else:
            lines.append("- none")
        lines.append("")

    return "\n".join(lines)


def schema_snapshot(target_schema: str | None, all_schemas: bool) -> None:
    """
    스키마 스냅샷 생성 메인 함수
    """
    with psycopg2.connect(DB_DSN) as conn:
        if all_schemas:
            schemas = _list_schemas(conn)
        else:
            schemas = [target_schema or DB_SCHEMA]

        schema_snapshots = []
        for sch in schemas:
            cols_rows, pk_rows, fk_rows = _fetch_schema_rows(conn, sch)
            schema_snapshots.append(_build_snapshot_for_schema(cols_rows, pk_rows, fk_rows, sch))

    snapshot_all = {
        "default_schema_env": DB_SCHEMA,
        "schemas": schema_snapshots,
    }

    # 저장
    OUTPUT_JSON.write_text(json.dumps(snapshot_all, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_TXT.write_text(_render_text(snapshot_all), encoding="utf-8")

    print("✅ schema snapshot 생성 완료")
    print("schemas:", [s["schema"] for s in schema_snapshots])
    print("output txt :", OUTPUT_TXT)
    print("output json:", OUTPUT_JSON)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", default=None, help="덤프할 스키마(기본: DB_SCHEMA)")
    parser.add_argument("--all-schemas", action="store_true", help="시스템 스키마 제외 전체 스키마 덤프")
    args = parser.parse_args()

    schema_snapshot(target_schema=args.schema, all_schemas=bool(args.all_schemas))