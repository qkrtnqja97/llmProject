#model_training/create_data/build_rag_templates.py
"""
[BUILD RAG TEMPLATES] 만족도=1 SQL 데이터 → 템플릿 라이브러리 생성 스크립트

📌 역할
- raw_log_erp_15000.csv(또는 gold_examples export CSV)에서
  질문(question)과 SQL(generated_sql 또는 final_sql)을 읽는다.
- SQL을 (sql_template + slots_json) 형태로 템플릿화(patternize)한다.
- 아래 3가지 산출물을 생성한다.

✅ 산출물
1) sql_template_library.csv
   - pattern_id(템플릿 ID), sql_template, slots_schema, usage_count, example_question
2) question_to_template_pairs.csv
   - question, pattern_id, slots_json
3) sql_templates_for_rag.jsonl
   - Chroma 업로드용 문서(JSONL)

📦 사용 라이브러리
- pandas: CSV 읽기/쓰기 및 그룹 집계
- json: slots_json / jsonl 생성
- hashlib: sql_template 해시로 pattern_id 생성
- pathlib.Path: 경로 처리
- create_data.slot_rules.patternize_sql: SQL 템플릿화 + 슬롯 추출
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import pandas as pd

from create_data.slot_rules import patternize_sql


def make_pattern_id(sql_template: str) -> str:
    """
    sql_template 텍스트를 기반으로 안정적인 pattern_id를 만드는 함수

    Args:
        sql_template: 공백 정규화된 SQL 템플릿 문자열

    Returns:
        str: pattern_id (예: PAT_1a2b3c4d5e6f)
    """
    h = hashlib.sha1(sql_template.encode("utf-8")).hexdigest()[:12]
    return f"PAT_{h}"


def _pick_sql_column(df: pd.DataFrame) -> str:
    """
    입력 CSV에서 SQL이 들어있는 컬럼명을 자동 선택하는 함수

    우선순위:
    1) generated_sql
    2) final_sql
    3) sql

    Args:
        df: 입력 데이터프레임

    Returns:
        str: 사용될 SQL 컬럼명

    Raises:
        ValueError: 적절한 SQL 컬럼을 찾지 못한 경우
    """
    candidates = ["generated_sql", "final_sql", "sql"]
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(
        f"SQL 컬럼을 찾지 못했습니다. 필요 컬럼 중 하나가 있어야 합니다: {candidates} / 현재 컬럼={list(df.columns)}"
    )


def build_rag_templates(
    input_csv: str,
    output_dir: str,
    question_col: str = "question",
    sql_col: Optional[str] = None,
) -> Tuple[int, int]:
    """
    CSV 기반으로 템플릿 라이브러리를 생성하는 메인 함수

    Args:
        input_csv: 입력 CSV 경로 (예: train_data/raw/raw_log_erp_15000.csv)
        output_dir: 산출물 저장 폴더 (예: train_data/rag_templates)
        question_col: 질문 컬럼명 (기본: question)
        sql_col: SQL 컬럼명(지정하지 않으면 자동 선택)

    Returns:
        (patterns, pairs)
        - patterns: 생성된 템플릿(pattern_id) 개수
        - pairs: question->pattern 매핑 개수
    """
    in_path = Path(input_csv).expanduser().resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"입력 CSV를 찾을 수 없습니다: {in_path}")

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    if question_col not in df.columns:
        raise ValueError(f"질문 컬럼이 없습니다: {question_col} / 현재 컬럼={list(df.columns)}")

    # SQL 컬럼 자동 선택
    sql_col_name = sql_col or _pick_sql_column(df)

    pairs_rows = []
    tpl_rows = []

    # --- row 단위 템플릿화 ---
    for _, row in df.iterrows():
        question = str(row[question_col]).strip()
        sql = str(row[sql_col_name]).strip()

        if not question or not sql:
            continue

        sql_template, slots = patternize_sql(sql)
        if not sql_template:
            continue

        pattern_id = make_pattern_id(sql_template)

        pairs_rows.append(
            {
                "question": question,
                "pattern_id": pattern_id,
                "slots_json": json.dumps(slots, ensure_ascii=False, sort_keys=True),
            }
        )

        tpl_rows.append(
            {
                "pattern_id": pattern_id,
                "sql_template": sql_template,
                "slots_schema": ", ".join(sorted(slots.keys())) if slots else "",
                "example_question": question,
            }
        )

    pairs_df = pd.DataFrame(pairs_rows)
    tpl_df = pd.DataFrame(tpl_rows)

    if pairs_df.empty or tpl_df.empty:
        raise RuntimeError("템플릿 생성 결과가 비었습니다. 입력 CSV 컬럼/내용을 확인하세요.")

    # --- pattern_id별 압축(라이브러리) ---
    lib_df = (
        tpl_df.groupby("pattern_id")
        .agg(
            sql_template=("sql_template", "first"),
            slots_schema=("slots_schema", "first"),
            usage_count=("pattern_id", "size"),
            example_question=("example_question", "first"),
        )
        .reset_index()
    )

    # --- 저장 경로 ---
    lib_path = out_dir / "sql_template_library.csv"
    pairs_path = out_dir / "question_to_template_pairs.csv"
    jsonl_path = out_dir / "sql_templates_for_rag.jsonl"

    lib_df.to_csv(lib_path, index=False, encoding="utf-8-sig")
    pairs_df.to_csv(pairs_path, index=False, encoding="utf-8-sig")

    # --- jsonl 생성 (Chroma ingest용 문서) ---
    with jsonl_path.open("w", encoding="utf-8") as f:
        for _, r in lib_df.iterrows():
            doc = {
                "pattern_id": r["pattern_id"],
                "sql_template": r["sql_template"],
                "slots_schema": r["slots_schema"],
                "usage_count": int(r["usage_count"]),
                "example_question": r["example_question"],
                # 검색 품질을 위해 text를 합쳐서 embedding 대상으로 사용
                "text": (
                    f"pattern_id: {r['pattern_id']}\n"
                    f"slots: {r['slots_schema']}\n"
                    f"example: {r['example_question']}\n"
                    f"sql: {r['sql_template']}"
                ),
            }
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    return (len(lib_df), len(pairs_df))


if __name__ == "__main__":
    """
    단독 실행 엔트리

    ✅ 기본 입력:
    - train_data/raw/raw_log_erp_15000.csv

    ✅ 기본 출력:
    - train_data/rag_templates/
      - sql_template_library.csv
      - question_to_template_pairs.csv
      - sql_templates_for_rag.jsonl
    """
    default_input = r"train_data\raw\raw_log_erp_15000.csv"
    default_out = r"train_data\rag_templates"

    patterns, pairs = build_rag_templates(
        input_csv=default_input,
        output_dir=default_out,
        question_col="question",
        sql_col=None,  # 자동 선택
    )

    print("✅ RAG 템플릿 생성 완료")
    print("input   :", default_input)
    print("output  :", default_out)
    print("patterns:", patterns)
    print("pairs   :", pairs)