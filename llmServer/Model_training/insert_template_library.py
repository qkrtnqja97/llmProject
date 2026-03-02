import psycopg2
from psycopg2.extras import RealDictCursor
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

PATTERN_ID = "PAT_AMT_MONTH_001"
SQL_TEMPLATE = (
    "SELECT {{part_number}} AS part_number, "
    "SUM(sale_quantity*actual_selling_price) AS total_amount "
    "FROM sales_orders "
    "WHERE part_number={{part_number}} "
    "AND EXTRACT(YEAR FROM sale_date)={{year}} "
    "AND EXTRACT(MONTH FROM sale_date)={{month}};"
)
SLOTS_SCHEMA = "month, part_number, year"
EXAMPLE_QUESTION = "2024년 3월 10M16SAU169I7G의 총 매출은?"

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")

        cur.execute(
            "SELECT pattern_id FROM sql_assistant.template_library WHERE pattern_id = %s",
            (PATTERN_ID,),
        )
        if cur.fetchone():
            print("✅ already exists in template_library:", PATTERN_ID)
        else:
            cur.execute(
                """
                INSERT INTO sql_assistant.template_library
                  (pattern_id, sql_template, slots_schema, example_question, usage_count, is_active, created_at, updated_at)
                VALUES
                  (%s, %s, %s, %s, 0, true, now(), now())
                """,
                (PATTERN_ID, SQL_TEMPLATE, SLOTS_SCHEMA, EXAMPLE_QUESTION),
            )
            print("✅ inserted into template_library:", PATTERN_ID)

    conn.commit()