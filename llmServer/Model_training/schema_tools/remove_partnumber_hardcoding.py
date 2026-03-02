import json
import re
from pathlib import Path

# schema_tools 폴더에서 실행 기준
JSONL_PATH = Path(r"..\train_data\rag_templates\sql_templates_for_rag.jsonl")

# SELECT 'XXXX' AS part_number  / SELECT "XXXX" AS part_number 형태 제거
RE_SELECT_PART = re.compile(
    r"SELECT\s+('.*?'|\".*?\")\s+AS\s+part_number",
    re.IGNORECASE | re.DOTALL,
)

def fix_sql(sql: str) -> str:
    # SELECT 절의 하드코딩 part_number를 slot으로 치환
    return RE_SELECT_PART.sub("SELECT {{part_number}} AS part_number", sql)

def main() -> None:
    if not JSONL_PATH.exists():
        raise FileNotFoundError(f"jsonl not found: {JSONL_PATH.resolve()}")

    lines = JSONL_PATH.read_text(encoding="utf-8").splitlines()
    out_lines = []
    changed = 0
    total = 0

    for line in lines:
        if not line.strip():
            continue
        total += 1
        obj = json.loads(line)

        sql = obj.get("sql_template", "")
        new_sql = fix_sql(sql)
        if new_sql != sql:
            obj["sql_template"] = new_sql
            changed += 1

        out_lines.append(json.dumps(obj, ensure_ascii=False))

    JSONL_PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"OK: {JSONL_PATH}")
    print(f"total: {total}")
    print(f"changed: {changed}")

if __name__ == "__main__":
    main()