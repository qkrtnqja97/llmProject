import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

dsn = os.getenv("DB_DSN") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
print("[env] dsn(raw) =", dsn)

if not dsn:
    raise SystemExit("❌ DSN is None. .env에 DB_DSN(또는 DATABASE_URL/DB_URL) 확인 필요")

dsn = dsn.replace("+psycopg2", "")
print("[env] dsn(psycopg2) =", dsn)

SQLS = {
    "C_schema_search_path": """
        SELECT current_schema() AS current_schema, current_schemas(true) AS schemas;
    """,
    "A_part_exists": """
        SELECT part_number, COUNT(*) AS cnt
        FROM sales_orders
        WHERE part_number = 'EN2210-BG1'
        GROUP BY part_number;
    """,
    "B_year_2024_stats": """
        SELECT MIN(sale_date) AS min_dt, MAX(sale_date) AS max_dt, COUNT(*) AS cnt
        FROM sales_orders
        WHERE EXTRACT(YEAR FROM sale_date) = 2024;
    """,
}

conn = psycopg2.connect(dsn)
try:
    # ✅ 핵심: 런타임과 동일하게 search_path 세팅
    with conn.cursor() as cur:
        cur.execute("SET search_path TO inventory_mgmt, public;")
    conn.commit()

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for name, sql in SQLS.items():
            print("\n==", name, "==")
            cur.execute(sql)
            rows = cur.fetchall()
            print("rows:", len(rows))
            if rows:
                print("preview:", rows[:5])
finally:
    conn.close()