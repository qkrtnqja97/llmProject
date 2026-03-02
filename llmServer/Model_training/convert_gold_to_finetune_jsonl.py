import json

IN_PATH = "train_data/gold_examples_export.jsonl"
OUT_PATH = "train_data/gold_finetune_messages.jsonl"

SYSTEM_PROMPT = "You are a SQL assistant for PostgreSQL. Return only SQL. Do not explain."

rows = 0
with open(IN_PATH, "r", encoding="utf-8") as f_in, open(OUT_PATH, "w", encoding="utf-8") as f_out:
    for line in f_in:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)

        question = r["question"]
        sql = r["final_sql"]

        rec = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
                {"role": "assistant", "content": sql},
            ]
        }
        f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        rows += 1

print(f"✅ converted {rows} rows -> {OUT_PATH}")