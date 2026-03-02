import psycopg2
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
        cur.execute("""
            ALTER TABLE sql_assistant.template_library
            ADD COLUMN IF NOT EXISTS gold_count INTEGER DEFAULT 0;
        """)
    conn.commit()

print("✅ template_library.gold_count column ensured")