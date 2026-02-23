import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from loaders.postgres_loader import open_tunnel, connect_postgres
from config.etl_config import POSTGRES_CONFIG
from sqlalchemy import text


def show_tables(engine):
    print("\n📦 [테이블 목록 조회]")

    query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{POSTGRES_CONFIG["schema"]}';
    """

    with engine.connect() as conn:
        tables = conn.execute(text(query)).fetchall()

    table_names = [t[0] for t in tables]

    for name in table_names:
        print(" -", name)

    return table_names


def preview_table(engine, table_name, limit=3):
    print(f"\n🔎 [{table_name}] 상위 {limit}개 데이터")

    query = f"""
        SELECT *
        FROM {POSTGRES_CONFIG["schema"]}.{table_name}
        LIMIT {limit};
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()
        rows = result.fetchall()

    print("컬럼:", list(columns))

    for row in rows:
        print(dict(zip(columns, row)))


if __name__ == "__main__":

    print("🚀 스키마 구조 분석 시작")

    engine,proc = connect_postgres()

    if engine is None:
        print("❌ DB 연결 실패")
        proc.terminate()
        exit()

    try:
        tables = show_tables(engine)

        for table in tables:
            preview_table(engine, table, limit=3)

    finally:
        proc.terminate()
        print("\n✅ 터널 종료")