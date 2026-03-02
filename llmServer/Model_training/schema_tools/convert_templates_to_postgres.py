import json, re
from pathlib import Path

src = Path(r"..\train_data\rag_templates\sql_templates_for_rag.jsonl")
dst = Path(r"..\train_data\rag_templates\sql_templates_for_rag.jsonl")  # 덮어쓰기

re_year = re.compile(r"strftime\(\s*'%Y'\s*,\s*(?P<col>(?:\w+\.)?(?:sale_date|purchase_date))\s*\)", re.IGNORECASE)
re_month = re.compile(r"strftime\(\s*'%m'\s*,\s*(?P<col>(?:\w+\.)?(?:sale_date|purchase_date))\s*\)", re.IGNORECASE)
re_yearmonth = re.compile(r"strftime\(\s*'%Y-%m'\s*,\s*(?P<col>(?:\w+\.)?(?:sale_date|purchase_date))\s*\)", re.IGNORECASE)
re_eq_quoted_int = re.compile(r"=\s*'(?P<num>\d+)'")

def convert(sql: str) -> str:
    s = sql
    s = re_yearmonth.sub(lambda m: f"to_char({m.group('col')}, 'YYYY-MM')", s)
    s = re_year.sub(lambda m: f"EXTRACT(YEAR FROM {m.group('col')})", s)
    s = re_month.sub(lambda m: f"EXTRACT(MONTH FROM {m.group('col')})", s)
    s = re_eq_quoted_int.sub(lambda m: f"= {int(m.group('num'))}", s)
    return s

lines = src.read_text(encoding="utf-8").splitlines()
out = []
for line in lines:
    if not line.strip():
        continue
    obj = json.loads(line)
    obj["sql_template"] = convert(obj.get("sql_template",""))
    out.append(json.dumps(obj, ensure_ascii=False))

dst.write_text("\n".join(out) + "\n", encoding="utf-8")
print("OK:", dst, "count=", len(out))