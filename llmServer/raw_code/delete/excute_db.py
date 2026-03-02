# DB 실행
def execute_db_node(state: AgentState):
    sql = state["sql_query"]

    # ✅ [#2] 화이트리스트 검증 + sqlglot 파싱 검증
    is_valid, reason = validate_sql(sql)
    if not is_valid:
        logger.warning(f"SQL 검증 실패: {reason} | SQL: {sql}")
        return {
            "db_result": f"Error: 보안 정책 위반 - {reason}",
            "error_history": state.get("error_history", []) + [reason],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # [4] Static Validator 강화 (컬럼소속 + GROUP BY + Cartesian + 테이블존재 통합)
    static_valid, static_reason, static_strategy = validate_sql_static(sql)
    if not static_valid:
        logger.warning(f"Static 검증 실패 [{static_strategy}]: {static_reason}")
        return {
            "db_result": f"Error: {static_reason}",
            "validation_errors": [static_reason],
            "retry_strategy": static_strategy,
            "error_history": state.get("error_history", []) + [static_reason],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    try:
        with engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {DB_SCHEMA}"))
            # ✅ [#8] LIMIT 적용 - 이미 LIMIT 있으면 래핑하지 않음 (ORDER BY 보존)
            has_limit = bool(re.search(r"\bLIMIT\b", sql, re.IGNORECASE))
            if has_limit:
                # 이미 LIMIT 있는 경우: 그대로 실행 (ORDER BY+LIMIT 조합 보호)
                safe_sql = sql
            else:
                # LIMIT 없는 경우: 서브쿼리로 감싸서 상한 적용
                safe_sql = f"SELECT * FROM ({sql}) AS _sub LIMIT {QUERY_RESULT_LIMIT}"
            df = pd.read_sql_query(text(safe_sql), conn)
        logger.info(f"쿼리 실행 성공 | 행 수: {len(df)}")
        # [6] Fewshot 품질관리 저장
        save_successful_sql(
            state.get("question", ""),
            sql,
            was_retried=state.get("retry_count", 0) > 0,
            retry_count=state.get("retry_count", 0),
        )
        # [10] Explainability 메타 구축
        ex_meta = build_explain_meta(sql, df, state.get("query_plan", {}))
        return {
            "df": df,
            "db_result": "SUCCESS",
            "retry_count": state.get("retry_count", 0),
            "explain_meta": ex_meta,
        }
    except Exception as e:
        logger.exception("쿼리 실행 오류")
        err_hint = rag_retrieve_error_hint(str(e))
        err_str = str(e)
        err_msg = err_str

        # 복잡 쿼리 실패 시 단순화 힌트 추가
        simplify_hint = ""
        if "syntax error" in err_str.lower() or "SyntaxError" in err_str:
            simplify_hint = " | 재시도 규칙: TO_DATE/DATE_TRUNC 중첩 금지. EXTRACT(YEAR FROM 컬럼)=연도, EXTRACT(QUARTER FROM 컬럼)=분기 처럼 단순하게 작성"
        if err_hint:
            err_msg += f" | 힌트: {err_hint}"
        if simplify_hint:
            err_msg += simplify_hint
            logger.info(f"단순화 힌트 적용")

        return {
            "db_result": f"Error: {err_str}",
            "error_history": state.get("error_history", []) + [err_msg],
            "retry_count": state.get("retry_count", 0) + 1,
        }


# ✅ [#2] SQL 허용 구문 화이트리스트 검증 함수
def validate_sql(sql: str) -> tuple[bool, str]:
    """SELECT / WITH 구문만 허용. sqlglot은 경고 로깅만 하고 실행은 허용."""
    first_token = sql.strip().upper().split()[0] if sql.strip() else ""
    if first_token not in ("SELECT", "WITH"):
        return False, f"허용되지 않은 구문: {first_token}"

    # sqlglot은 파싱 실패 시 차단하지 않고 경고만 남김
    try:
        sqlglot.parse_one(sql, dialect="postgres")
    except sqlglot.errors.ParseError as e:
        logger.warning(f"sqlglot 파싱 경고 (실행은 계속): {str(e)[:200]}")
    except Exception as e:
        logger.warning(f"sqlglot 예외 (실행은 계속): {str(e)[:200]}")

    return True, ""


# ==========================================
# [4] SQL Static Validator 강화
# ==========================================
def validate_sql_static(sql: str) -> tuple[bool, str, str]:
    """
    Python 레벨 SQL 구조 검증
    Returns: (is_valid, error_message, retry_strategy)
    """
    sql_upper = sql.upper()
    errors = []
    strategy = "syntax"

    # 1. SELECT * 금지
    if re.search(r"SELECT\s+\*", sql_upper):
        errors.append("SELECT * 금지. 필요한 컬럼을 명시하세요.")
        strategy = "syntax"

    # 2. GROUP BY 누락 검사 (집계함수 + 비집계 컬럼 혼합)
    has_agg = bool(re.search(r"\b(SUM|AVG|COUNT|MAX|MIN)\s*\(", sql_upper))
    has_grp = bool(re.search(r"\bGROUP\s+BY\b", sql_upper))
    has_win = bool(re.search(r"\bOVER\s*\(", sql_upper))
    if has_agg and not has_grp and not has_win:
        sel_m = re.search(r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
        if sel_m:
            cleaned = re.sub(
                r"(SUM|AVG|COUNT|MAX|MIN)\s*\([^)]+\)",
                "",
                sel_m.group(1),
                flags=re.IGNORECASE,
            )
            non_agg = [
                c.strip()
                for c in cleaned.split(",")
                if c.strip()
                and c.strip() not in ("", "*")
                and not c.strip().upper().startswith("AS")
            ]
            if non_agg:
                errors.append(f"GROUP BY 누락: 비집계 컬럼 존재. GROUP BY 추가 필요.")
                strategy = "logic"

    # 3. Cartesian Product 감지 (JOIN ON 조건 부족)
    join_cnt = len(re.findall(r"\bJOIN\b", sql_upper))
    on_cnt = len(re.findall(r"\bON\b|\bUSING\b", sql_upper))
    if join_cnt > 0 and on_cnt < join_cnt:
        errors.append(
            f"Cartesian Product 위험: JOIN {join_cnt}개, ON {on_cnt}개. ON 조건 추가 필요."
        )
        strategy = "logic"

    # 4. 존재하지 않는 테이블 참조
    sql_clean = re.sub(
        r"EXTRACT\s*\([^)]+\)", "EXTRACT_PLACEHOLDER", sql, flags=re.IGNORECASE
    )

    # [기능] WITH 절(CTE)에서 생성된 가상 테이블 이름을 정규식으로 추출
    cte_names = re.findall(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\(", sql_clean, re.IGNORECASE
    )

    ref_tables = re.findall(
        r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_clean, re.IGNORECASE
    )
    skip_aliases = {
        "_sub",
        "sr",
        "cum",
        "cte",
        "sub",
        "t",
        "a",
        "b",
        "extract_placeholder",
    }

    # [기능] 추출한 CTE 이름을 테이블 검증 예외 목록에 병합하여 에러 방지
    skip_aliases.update([name.lower() for name in cte_names])

    for tbl in ref_tables:
        if tbl.lower() not in COLUMN_MAP and tbl.lower() not in skip_aliases:
            errors.append(f"테이블 '{tbl}' DB에 없음. 유효: {list(COLUMN_MAP.keys())}")
            strategy = "table_missing"

    # 5. 컬럼 소속 검증 (기존 함수 통합)
    col_valid, col_reason = validate_column_ownership(sql)
    if not col_valid:
        errors.append(col_reason)
        strategy = "column_missing"

    # 6. 불필요한 JOIN (JOIN 후 해당 별칭 미사용)
    join_aliases = re.findall(
        r"JOIN\s+[a-zA-Z_][a-zA-Z0-9_]*\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE,
    )
    for alias in join_aliases:
        # [기능] ON, USING 등의 SQL 예약어는 별칭이 아니므로 검사에서 제외
        if alias.upper() in ("ON", "USING"):
            continue

        usage = re.findall(rf"\b{re.escape(alias)}\.[a-zA-Z_]", sql, re.IGNORECASE)
        if not usage:
            errors.append(f"불필요한 JOIN: '{alias}' JOIN 후 컬럼 미사용.")

    # 7. 테이블 JOIN 키 매핑 정적 검증 (LLM 환각 방지)
    # [기능] 사전 정의된 VALID_JOINS 규칙을 통해 잘못된 컬럼 간의 JOIN을 원천 차단
    # [메모리 최적화] 대용량 쿼리 문자열 처리 시 리스트 전체를 반환하는 findall 대신
    # 제너레이터 방식인 finditer를 사용하여 메모리 점유율을 최소화
    alias_map = {}
    for m in re.finditer(
        r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE,
    ):
        tbl, alias = m.group(1).lower(), m.group(2).lower()
        if alias.upper() not in (
            "ON",
            "USING",
            "WHERE",
            "GROUP",
            "ORDER",
            "LEFT",
            "RIGHT",
            "INNER",
        ):
            alias_map[alias] = tbl
            alias_map[tbl] = tbl

    # ON 절 검증 시에도 메모리 최적화를 위해 finditer 적용
    for on_clause in re.finditer(
        r"ON\s+([a-zA-Z_]+)\.([a-zA-Z_]+)\s*=\s*([a-zA-Z_]+)\.([a-zA-Z_]+)",
        sql,
        re.IGNORECASE,
    ):
        a1, c1, a2, c2 = on_clause.groups()
        t1, t2 = alias_map.get(a1.lower()), alias_map.get(a2.lower())

        if t1 and t2 and t1 != t2:
            pair = frozenset([t1, t2])
            expected_key = VALID_JOINS.get(pair)

            # 사전에 정의된 관계일 경우, 양쪽 컬럼이 모두 지정된 키와 일치하는지 확인
            if expected_key:
                if c1.lower() != expected_key or c2.lower() != expected_key:
                    errors.append(
                        f"잘못된 JOIN: '{t1}'과 '{t2}'는 '{expected_key}' 컬럼으로 연결해야 합니다."
                    )
                    strategy = "logic"

    if errors:
        return False, " | ".join(errors), strategy
    return True, "", "none"


# ==========================================
# [10] Explainability
# ==========================================
def build_explain_meta(sql: str, df, plan: dict) -> dict:
    """실행 결과에서 설명 메타 추출"""
    tables_used = list(
        set(re.findall(r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE))
    )
    agg_matches = re.findall(
        r"(SUM|AVG|COUNT|MAX|MIN)\s*\(([^)]+)\)", sql, re.IGNORECASE
    )
    aggregations = [f"{fn}({col.strip()})" for fn, col in agg_matches]

    filters_applied = []
    where_m = re.search(
        r"WHERE\s+(.*?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)",
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if where_m:
        raw_where = where_m.group(1).strip()
        filters_applied = [
            f.strip()
            for f in re.split(r"\bAND\b|\bOR\b", raw_where, flags=re.IGNORECASE)
            if f.strip()
        ]

    return {
        "sql_used": sql,
        "tables_used": tables_used,
        "aggregations": aggregations,
        "filters_applied": filters_applied[:5],
        "group_by": (plan or {}).get("group_by", "none"),
        "row_count": len(df) if df is not None else 0,
        "intent_summary": (plan or {}).get("intent_summary", ""),
    }


EXPLAIN_TRIGGERS = [
    "어떻게 계산",
    "왜 이 값",
    "어떻게 나온",
    "설명해줘",
    "근거",
    "어떻게 구한",
]


def generate_explanation(meta: dict, question: str) -> str:
    lines = [f"**'{question}'** 계산 방법:"]
    if meta.get("tables_used"):
        lines.append(f"- 사용 테이블: `{'`, `'.join(meta['tables_used'])}`")
    if meta.get("aggregations"):
        lines.append(f"- 집계 방식: {', '.join(meta['aggregations'])}")
    if meta.get("filters_applied"):
        lines.append(f"- 적용 필터: {' AND '.join(meta['filters_applied'][:3])}")
    if meta.get("group_by") and meta["group_by"] != "none":
        lines.append(f"- 그룹 기준: {meta['group_by']}")
    lines.append(f"- 결과 행수: {meta.get('row_count', 0)}건")
    if meta.get("sql_used"):
        lines.append(f"\n```sql\n{meta['sql_used']}\n```")
    return "\n".join(lines)


# ==========================================
# SQL 컬럼 소속 검증 (방향2: 코드 레벨 사전 차단)
# ==========================================
def validate_column_ownership(sql: str) -> tuple[bool, str]:
    """
    SQL에서 테이블별칭.컬럼 패턴을 추출해서
    실제 DB COLUMN_MAP과 대조 → 잘못된 소속 감지
    """
    if not COLUMN_MAP:
        return True, ""

    import re

    # 테이블 별칭 → 실제 테이블명 매핑 (FROM/JOIN 절 파싱)
    alias_map = {}
    # FROM table alias, JOIN table alias 패턴 추출
    table_pattern = re.compile(
        r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)",
        re.IGNORECASE,
    )
    for m in table_pattern.finditer(sql):
        tbl, alias = m.group(1).lower(), m.group(2).lower()
        alias_map[alias] = tbl
        alias_map[tbl] = tbl  # 별칭 없이 테이블명 직접 사용도 처리

    if not alias_map:
        return True, ""

    # alias.column 패턴 추출
    col_ref_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.(\w+)\b")
    errors = []

    for m in col_ref_pattern.finditer(sql):
        alias, col = m.group(1).lower(), m.group(2).lower()
        if alias not in alias_map:
            continue
        actual_table = alias_map[alias]
        if actual_table not in COLUMN_MAP:
            continue
        valid_cols = [c.lower() for c in COLUMN_MAP[actual_table]]
        if col not in valid_cols:
            # 이 컬럼이 실제로 어느 테이블에 있는지 찾기
            found_in = [
                t for t, cols in COLUMN_MAP.items() if col in [c.lower() for c in cols]
            ]
            hint = f"'{col}'은 '{actual_table}'에 없음"
            if found_in:
                hint += f" → '{found_in[0]}' 테이블 소속. JOIN 필요"
            errors.append(hint)

    if errors:
        err_msg = "컬럼 소속 오류: " + " | ".join(errors)
        return False, err_msg

    return True, ""
