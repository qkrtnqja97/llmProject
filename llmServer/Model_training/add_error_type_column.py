import psycopg2
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

DDL = """
ALTER TABLE sql_assistant.request_logs
ADD COLUMN IF NOT EXISTS error_type VARCHAR(50);
"""

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
        cur.execute(DDL)
    conn.commit()

print("✅ request_logs.error_type column ensured")