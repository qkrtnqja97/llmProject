import psycopg2
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")

        # gold_count를 0으로 초기화
        cur.execute("""
            UPDATE sql_assistant.template_library
            SET gold_count = 0
            WHERE gold_count IS NOT NULL;
        """)

        # gold_examples에서 pattern_id별 count 집계해서 반영
        cur.execute("""
            UPDATE sql_assistant.template_library t
            SET gold_count = g.cnt,
                updated_at = now()
            FROM (
                SELECT pattern_id, COUNT(*)::int AS cnt
                FROM sql_assistant.gold_examples
                GROUP BY pattern_id
            ) g
            WHERE t.pattern_id = g.pattern_id;
        """)

    conn.commit()

print("✅ gold_count backfill done")