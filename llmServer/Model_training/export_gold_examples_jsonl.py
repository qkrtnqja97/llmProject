import json
import psycopg2
from psycopg2.extras import RealDictCursor
from schema_tools.a_db_config import DB_DSN, DB_SEARCH_PATH

OUT_PATH = "train_data/gold_examples_export.jsonl"

with psycopg2.connect(DB_DSN) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SET search_path TO {DB_SEARCH_PATH}")
        cur.execute("""
            SELECT
              ge.example_id,
              ge.created_at,
              ge.question,
              ge.pattern_id,
              ge.slots_json,
              ge.final_sql
            FROM sql_assistant.gold_examples ge
            ORDER BY ge.created_at ASC;
        """)
        rows = cur.fetchall()

with open(OUT_PATH, "w", encoding="utf-8") as f:
    for r in rows:
        # jsonl 레코드(학습/분석 공용)
        rec = {
            "example_id": str(r["example_id"]),
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "question": r["question"],
            "pattern_id": r["pattern_id"],
            "slots_json": r["slots_json"] or {},
            "final_sql": r["final_sql"],
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"✅ exported {len(rows)} rows -> {OUT_PATH}")