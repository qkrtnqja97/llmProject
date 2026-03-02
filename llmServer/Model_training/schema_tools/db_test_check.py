#db_test_check.py
""" 
inspect_tables.py 역할: 
    ** 디비 파트 
    - PostgreSQL 서버(DB)에 실제로 접속 가능한지 테스트 
    - 현재 접속 대상(DB_DSN)과 스키마(DB_SCHEMA)가 올바른지 빠르게 검증 
    ** 스키마 파트 
    - 지정한 스키마(DB_SCHEMA) 기준으로 테이블/컬럼 정보를 조회해서 출력 
    - "현재 DB에 어떤 테이블/컬럼이 있는지" 빠르게 확인하는 도구 

사용 라이브러리: 
    - psycopg2: PostgreSQL 연결/쿼리 실행 (팀 표준) 
    - a_db_config: .env에서 읽은 DB_DSN/DB_SCHEMA 

제공 주요 기능: 
    ** 디비 파트 
        1) 스키마 내 테이블 목록 조회 
        2) 테이블별 컬럼명/타입/nullable 출력 
        3) (선택) 특정 테이블만 보고 싶을 때 whitelist 필터 적용 가능 
    ** 스키마 파트 
        1) SELECT version() 실행으로 접속 확인 
        2) current_database(), current_schema() 확인 
        3) 설정된 DB_SCHEMA 존재 여부 확인 
"""

import psycopg2
from a_db_config import DB_DSN, DB_SCHEMA


def test_connection() -> None:
    """
    DB 연결 및 기본 검증을 수행하는 함수

    Returns:
        None
    """
    try:
        # psycopg2.connect: DSN 문자열로 DB 접속
        with psycopg2.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                # 1) DB 접속 확인: 버전
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]

                # 2) 현재 DB / 스키마 확인
                cur.execute("SELECT current_database(), current_schema();")
                db_name, cur_schema = cur.fetchone()

                # 3) 설정된 DB_SCHEMA가 실제로 존재하는지 확인
                cur.execute(
                    """
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name = %s;
                    """,
                    (DB_SCHEMA,)
                )
                schema_exists = cur.fetchone() is not None

        print("✅ DB 연결 성공")
        print("PostgreSQL Version :", version)
        print("Current Database   :", db_name)
        print("Current Schema     :", cur_schema)
        print("Target DB_SCHEMA   :", DB_SCHEMA)
        print("DB_SCHEMA Exists   :", schema_exists)

        if not schema_exists:
            print("⚠ 경고: DB_SCHEMA가 DB에 존재하지 않습니다. .env의 DB_SCHEMA 값을 확인하세요.")

    except Exception as e:
        print("DB 연결 실패")
        print("Error:", e)


# 보고 싶은 테이블만 제한하고 싶으면 여기에 테이블명을 넣으면 됨.
# 비워두면(=[]) 스키마 내 모든 테이블을 출력한다.
TABLE_WHITELIST = []  # 예: ["products", "inventory", "warehouses"]


def inspect_tables() -> None:
    """
    DB_SCHEMA 기준으로 테이블/컬럼 정보를 출력하는 함수

    Returns:
        None
    """
    query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
    """

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (DB_SCHEMA,))
            rows = cur.fetchall()

    if not rows:
        print(f"⚠ 스키마 '{DB_SCHEMA}'에서 조회된 컬럼이 없습니다.")
        print("   - DB_SCHEMA 값이 맞는지 확인하세요.")
        return

    current_table = None
    printed_any = False

    for table_name, column_name, data_type, is_nullable, pos in rows:
        # whitelist 적용
        if TABLE_WHITELIST and table_name not in TABLE_WHITELIST:
            continue

        if table_name != current_table:
            print(f"\n Table: {table_name}")
            current_table = table_name
            printed_any = True

        nullable_flag = "NULL" if is_nullable == "YES" else "NOT NULL"
        print(f"   └─ {pos:02d}. {column_name} ({data_type}) {nullable_flag}")

    if TABLE_WHITELIST and not printed_any:
        print("⚠ TABLE_WHITELIST에 지정한 테이블이 스키마에 없거나 조회되지 않았습니다.")
        print("   TABLE_WHITELIST 값을 확인하세요.")


if __name__ == "__main__":
    print(f"[inspect_tables] Target schema = {DB_SCHEMA}")
    if TABLE_WHITELIST:
        print(f"[inspect_tables] TABLE_WHITELIST = {TABLE_WHITELIST}")
    test_connection()    
    inspect_tables()