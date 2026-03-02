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
            "retry_count": state.get("retry_count", 0) + 1
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
            "retry_count": state.get("retry_count", 0) + 1
        }

    try:
        with engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {DB_SCHEMA}"))
            # ✅ [#8] LIMIT 적용 - 이미 LIMIT 있으면 래핑하지 않음 (ORDER BY 보존)
            has_limit = bool(re.search(r'\bLIMIT\b', sql, re.IGNORECASE))
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
            state.get("question", ""), sql,
            was_retried=state.get("retry_count", 0) > 0,
            retry_count=state.get("retry_count", 0)
        )
        # [10] Explainability 메타 구축
        ex_meta = build_explain_meta(sql, df, state.get("query_plan", {}))
        return {"df": df, "db_result": "SUCCESS",
                "retry_count": state.get("retry_count", 0),
                "explain_meta": ex_meta}
    except Exception as e:
        logger.exception("쿼리 실행 오류")
        err_hint = rag_retrieve_error_hint(str(e))
        err_str  = str(e)
        err_msg  = err_str

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
            "retry_count": state.get("retry_count", 0) + 1
        }
