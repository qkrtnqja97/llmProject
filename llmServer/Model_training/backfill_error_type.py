import psycopg2
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")

        # 성공 케이스 NULL -> OK
        cur.execute("""
            UPDATE sql_assistant.request_logs
            SET error_type = 'OK'
            WHERE error_type IS NULL
              AND execution_success = true;
        """)

        # 실패 케이스 NULL -> 키워드 기반 분류
        cur.execute("""
            UPDATE sql_assistant.request_logs
            SET error_type = 'UNSUPPORTED_TERM'
            WHERE error_type IS NULL
              AND execution_success = false
              AND error_message ILIKE '%미지원 용어 감지%';
        """)

        cur.execute("""
            UPDATE sql_assistant.request_logs
            SET error_type = 'TEMPLATE_NOT_FOUND'
            WHERE error_type IS NULL
              AND execution_success = false
              AND error_message ILIKE '%템플릿 검색 실패%';
        """)

        cur.execute("""
            UPDATE sql_assistant.request_logs
            SET error_type = 'SAFETY_BLOCK'
            WHERE error_type IS NULL
              AND execution_success = false
              AND (
                    error_message ILIKE '%위험 sql%'
                 OR error_message ILIKE '%멀티 스테이트먼트%'
              );
        """)

        # 나머지 실패 NULL -> UNKNOWN
        cur.execute("""
            UPDATE sql_assistant.request_logs
            SET error_type = 'UNKNOWN'
            WHERE error_type IS NULL
              AND execution_success = false;
        """)

    conn.commit()

print("✅ backfill done")