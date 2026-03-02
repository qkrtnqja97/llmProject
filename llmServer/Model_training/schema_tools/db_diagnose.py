"""
[DB_DIAGNOSE] 현재 연결된 DB 정보 및 스키마 점검 스크립트

역할:
- 현재 DB_DSN 기준으로 실제 연결된 DB 정보 출력
- 사용자 스키마 목록 조회
- 각 스키마별 테이블 개수 출력

왜 필요?
- "팀 DB가 아니라 내 로컬 DB를 보고 있는지" 확인
- "스키마가 왜 안 보이는지" 즉시 진단
"""

from __future__ import annotations

import psycopg2
from schema_tools.a_db_config import DB_DSN


def main() -> None:
    print("🔎 DB 진단 시작")
    print("DB_DSN =", DB_DSN)
    print("-" * 60)

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:

            # 1️⃣ 현재 연결된 DB 정보
            cur.execute("""
                SELECT
                    inet_server_addr(),
                    inet_server_port(),
                    current_database(),
                    current_user,
                    version()
            """)
            info = cur.fetchone()

            print("📌 연결 정보")
            print(" - server_addr :", info[0])
            print(" - server_port :", info[1])
            print(" - database    :", info[2])
            print(" - user        :", info[3])
            print(" - version     :", info[4].split(",")[0])
            print()

            # data_directory (실제 물리 DB 경로)
            cur.execute("SHOW data_directory;")
            print(" - data_directory :", cur.fetchone()[0])
            print("-" * 60)

            # 2️⃣ 사용자 스키마 목록
            cur.execute("""
                SELECT nspname
                FROM pg_namespace
                WHERE nspname NOT LIKE 'pg_%'
                  AND nspname <> 'information_schema'
                ORDER BY 1;
            """)
            schemas = [r[0] for r in cur.fetchall()]

            print("📂 사용자 스키마 목록")
            if not schemas:
                print(" - 없음")
            else:
                for s in schemas:
                    print(" -", s)

            print("-" * 60)

            # 3️⃣ 각 스키마별 테이블 개수
            print("📊 스키마별 테이블 수")
            for s in schemas:
                cur.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                      AND table_type = 'BASE TABLE';
                """, (s,))
                count = cur.fetchone()[0]
                print(f" - {s} : {count} tables")

    print("-" * 60)
    print("✅ DB 진단 완료")


if __name__ == "__main__":
    main()