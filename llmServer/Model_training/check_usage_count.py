import psycopg2
from psycopg2.extras import RealDictCursor
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
        cur.execute("""
            SELECT pattern_id, usage_count, gold_count, is_active, updated_at
            FROM sql_assistant.template_library
            ORDER BY pattern_id;
        """)
        rows = cur.fetchall()

if not rows:
    print("❌ template_library 비어있음")
else:
    for r in rows:
        print(r)