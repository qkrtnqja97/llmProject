import psycopg2
from psycopg2.extras import RealDictCursor
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
        cur.execute("""
            SELECT
              request_id,
              created_at,
              question,
              execution_success,
              selected_pattern_id,
              row_count,
              user_satisfaction,
              error_type
            FROM sql_assistant.request_logs
            ORDER BY created_at DESC
            LIMIT 5;
        """)
        rows = cur.fetchall()

for r in rows:
    print(r)