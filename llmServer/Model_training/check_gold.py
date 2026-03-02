import psycopg2
from psycopg2.extras import RealDictCursor
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")

        # ✅ 추가: 총 건수 확인
        cur.execute("SELECT COUNT(*) AS cnt FROM sql_assistant.gold_examples;")
        print("gold_examples count =", cur.fetchone()["cnt"])
        
        cur.execute("""
            SELECT example_id, created_at, pattern_id, question
            FROM sql_assistant.gold_examples
            ORDER BY created_at DESC
            LIMIT 5;
        """)
        rows = cur.fetchall()

if not rows:
    print("❌ gold_examples 비어있음")
else:
    for r in rows:
        print(r)