#convert_csv2jsonl.py
"""
📌 역할:
- CSV(원본 로그/목업 데이터)를 LLM SFT 학습용 JSONL(prompt/completion)로 변환
- schema_snapshot.txt를 프롬프트에 포함하여 (schema + question) → SQL 학습 데이터 생성
- 기본 경로를 코드에 내장하여 CLI 없이도 실행 가능
- 필요 시 CLI 인자로 경로를 덮어쓸 수 있음

📦 사용 라이브러리(표준 라이브러리만 사용):
- argparse: CLI 인자 처리
- csv: CSV 읽기
- json: JSONL 쓰기
- pathlib.Path: 파일 경로/입출력
- re: 간단 품질 체크(SELECT *, LIMIT, 세미콜론 등)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


# =============================
# 기본 경로 설정 (프로젝트 기준)
# =============================
DEFAULT_CSV = Path("../train_data/raw/mock_traces_10000_satisfaction1.csv")
DEFAULT_SCHEMA = Path("train_data/inventory_schema_snapshot.txt")
DEFAULT_OUT = Path("train_data/train_sft.jsonl")

DEFAULT_QUESTION_COL = "question"
DEFAULT_SQL_COL = "generated_sql"


# =============================
# 프롬프트 템플릿 (SQL-only 강제)
# =============================
# ✅ 프롬프트 지시문은 영어로 유지(일관성/강제력 ↑)
# ✅ 질문 데이터는 한국어여도 상관 없음
PROMPT_TEMPLATE = """You are a SQL generator for PostgreSQL.
Rules:
- Output SQL only. No explanation.
- Use only tables/columns from the schema snapshot.
- Prefer safe SELECT queries.
- Add LIMIT if the result could be large.

### SCHEMA
{schema_snapshot}

### QUESTION
{question}

### OUTPUT (SQL only)
"""


def _parse_bool(v: str) -> bool:
    """
    문자열을 boolean으로 안전하게 파싱하는 유틸 함수

    Args:
        v (str): CSV에서 읽은 값

    Returns:
        bool: True/False
    """
    if v is None:
        return False
    return str(v).strip().lower() in ("true", "1", "yes", "y", "t")


def _quality_checks(sql_text: str) -> dict:
    """
    SQL 품질 체크(간단 버전)

    체크 항목:
    - SELECT * 사용 여부
    - LIMIT 포함 여부
    - 세미콜론 포함 여부(끝에 ;)

    Args:
        sql_text (str): SQL 문자열

    Returns:
        dict: 체크 결과
    """
    s = (sql_text or "").strip()
    return {
        "is_empty": len(s) == 0,
        "has_select_star": bool(re.search(r"select\s+\*", s, re.IGNORECASE)),
        "has_limit": bool(re.search(r"\blimit\b", s, re.IGNORECASE)),
        "ends_with_semicolon": s.endswith(";"),
    }


def convert_csv_to_jsonl(
    csv_path: Path,
    schema_path: Path,
    out_path: Path,
    filter_success_sat1: bool,
    sql_column: str,
    question_column: str,
    report_quality: bool,
) -> None:
    """
    CSV -> JSONL 변환 메인 함수

    Args:
        csv_path (Path): 입력 CSV 경로
        schema_path (Path): schema_snapshot 텍스트 파일 경로
        out_path (Path): 출력 JSONL 경로
        filter_success_sat1 (bool): execution_success=true AND user_satisfaction=1 필터 적용 여부(컬럼이 존재할 때만 적용)
        sql_column (str): SQL 컬럼명 (기본: generated_sql)
        question_column (str): 질문 컬럼명 (기본: question)
        report_quality (bool): 품질 체크 리포트 출력 여부

    Returns:
        None
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일이 없습니다: {csv_path}")
    if not schema_path.exists():
        raise FileNotFoundError(f"schema_snapshot 파일이 없습니다: {schema_path}")

    schema_snapshot = schema_path.read_text(encoding="utf-8").strip()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    kept = 0

    # 품질 체크 집계
    qc = {
        "empty_sql": 0,
        "select_star": 0,
        "no_limit": 0,
        "no_semicolon": 0,
    }

    with csv_path.open("r", encoding="utf-8", newline="") as f_in, out_path.open("w", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        headers = set(reader.fieldnames or [])

        # 컬럼 존재 확인
        if question_column not in headers:
            raise ValueError(f"CSV에 '{question_column}' 컬럼이 없습니다. 현재 컬럼: {sorted(headers)}")
        if sql_column not in headers:
            raise ValueError(f"CSV에 '{sql_column}' 컬럼이 없습니다. 현재 컬럼: {sorted(headers)}")

        has_success = "execution_success" in headers
        has_sat = "user_satisfaction" in headers

        for row in reader:
            total += 1

            # (선택) 성공/만족 필터 적용
            if filter_success_sat1 and has_success and has_sat:
                success_ok = _parse_bool(row.get("execution_success"))
                sat_ok = str(row.get("user_satisfaction", "")).strip() == "1"
                if not (success_ok and sat_ok):
                    continue

            question = str(row.get(question_column, "")).strip()
            sql_text = str(row.get(sql_column, "")).strip()

            # 품질 체크(선택)
            if report_quality:
                q = _quality_checks(sql_text)
                if q["is_empty"]:
                    qc["empty_sql"] += 1
                    continue
                if q["has_select_star"]:
                    qc["select_star"] += 1
                if not q["has_limit"]:
                    qc["no_limit"] += 1
                if not q["ends_with_semicolon"]:
                    qc["no_semicolon"] += 1

            prompt = PROMPT_TEMPLATE.format(schema_snapshot=schema_snapshot, question=question)

            record = {"prompt": prompt, "completion": sql_text}
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            kept += 1

    print("✅ convert_csv2jsonl 완료")
    print(f"- input : {csv_path}")
    print(f"- schema: {schema_path}")
    print(f"- output: {out_path}")
    print(f"- total rows: {total}")
    print(f"- kept rows : {kept}")

    if report_quality:
        print("\n[품질 리포트]")
        print(f"- empty_sql skipped : {qc['empty_sql']}")
        print(f"- select * count    : {qc['select_star']}")
        print(f"- no LIMIT count    : {qc['no_limit']}")
        print(f"- no semicolon      : {qc['no_semicolon']}")


def main() -> None:
    """
    CLI 엔트리포인트:
    - CLI 인자 없으면 기본 경로(DEFAULT_*) 사용
    - 필요 시 인자로 경로/컬럼명 덮어쓰기 가능
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="입력 CSV 파일 경로 (없으면 기본 경로 사용)")
    ap.add_argument("--schema", help="schema_snapshot 텍스트 파일 경로 (없으면 기본 경로 사용)")
    ap.add_argument("--out", help="출력 JSONL 파일 경로 (없으면 기본 경로 사용)")

    ap.add_argument("--filter_success_sat1", action="store_true",
                    help="CSV에 execution_success/user_satisfaction이 있으면 (true,1)만 필터링")
    ap.add_argument("--sql_col", default=DEFAULT_SQL_COL, help=f"SQL 컬럼명 (기본: {DEFAULT_SQL_COL})")
    ap.add_argument("--q_col", default=DEFAULT_QUESTION_COL, help=f"질문 컬럼명 (기본: {DEFAULT_QUESTION_COL})")
    ap.add_argument("--report_quality", action="store_true",
                    help="품질 체크 리포트 출력(SELECT*, LIMIT, 세미콜론 등)")

    args = ap.parse_args()

    csv_path = Path(args.csv) if args.csv else DEFAULT_CSV
    schema_path = Path(args.schema) if args.schema else DEFAULT_SCHEMA
    out_path = Path(args.out) if args.out else DEFAULT_OUT

    convert_csv_to_jsonl(
        csv_path=csv_path,
        schema_path=schema_path,
        out_path=out_path,
        filter_success_sat1=args.filter_success_sat1,
        sql_column=args.sql_col,
        question_column=args.q_col,
        report_quality=args.report_quality,
    )


if __name__ == "__main__":
    main()