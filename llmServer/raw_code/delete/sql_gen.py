# 지능형 SQL 생성
def generate_sql_node(state: AgentState):
  
    q = state["refined_question"]

    # 업무 맥락 주입 (후속질문 해석용)
    work_ctx = st.session_state.get("work_context", [])
    if work_ctx:
        recent = work_ctx[-6:]
        lines = []
        for m in recent:
            role = "사용자" if m["role"] == "user" else "AI답변"
            lines.append(f"{role}: {m['content'][:150]}")

        # ── 후속 질문 파라미터 치환 ──────────────────────────────
        # "23년은?", "1분기는?" 처럼 파라미터만 바뀐 짧은 질문을
        # 이전 질문 구조에 새 파라미터를 대입해 완성된 질문으로 재조립
        prev_user_msgs = [m["content"] for m in recent if m["role"] == "user"]
        prev_q = prev_user_msgs[-2] if len(prev_user_msgs) >= 2 else ""

        if prev_q and len(q.replace(" ", "")) <= 12:
            new_q = q

            # 연도 치환: "23년은?" → 이전 질문의 연도를 23으로 교체
            year_match = re.search(r'(\d{2,4})년', q)
            if year_match:
                new_year = year_match.group(1)
                if len(new_year) == 2:
                    new_year = f"20{new_year}"
                short_year = new_year[-2:]
                rebuilt = re.sub(r'\d{2,4}년', f"{short_year}년", prev_q)
                new_q = rebuilt
                logger.info(f"후속 연도치환: '{q}' → '{new_q}'")

            # 분기 치환: "2분기는?" → 이전 질문의 분기를 2로 교체
            elif re.search(r'([1-4])분기', q):
                qtr = re.search(r'([1-4])분기', q).group(1)
                if '분기' in prev_q:
                    rebuilt = re.sub(r'[1-4]분기', f"{qtr}분기", prev_q)
                else:
                    rebuilt = prev_q + f" ({qtr}분기 기준)"
                new_q = rebuilt
                logger.info(f"후속 분기치환: '{q}' → '{new_q}'")

            # 카테고리 치환: "저항은?", "IC는?" 등
            elif any(kw in q for kw in ["IC", "저항", "커패시터", "캐패시터", "FET", "트랜지스터"]):
                for kw in ["IC", "저항", "커패시터", "캐패시터", "FET", "트랜지스터"]:
                    if kw in q:
                        new_q = prev_q + f" (카테고리: {kw})"
                        logger.info(f"후속 카테고리치환: '{q}' → '{new_q}'")
                        break

            # 집계단위 치환: "부품단위로", "부품번호로" → part_number 단위로 재질의
            elif any(kw in q for kw in ["부품단위", "부품번호", "part_number", "개별로", "품목단위"]):
                new_q = prev_q + " (part_number 개별 부품 단위로, GROUP BY part_number)"
                logger.info(f"후속 부품단위치환: '{q}' → '{new_q}'")

            # 카테고리단위 치환: "카테고리단위로", "종류별로"
            elif any(kw in q for kw in ["카테고리단위", "카테고리별", "종류별", "description단위"]):
                new_q = prev_q + " (description 카테고리 단위로, GROUP BY description)"
                logger.info(f"후속 카테고리단위치환: '{q}' → '{new_q}'")

            if new_q != q:
                q = new_q

        # 대명사 치환: "이 제품", "해당 제품" → part_number
        PRONOUN_TRIGGERS = ["이 제품", "해당 제품", "그 제품", "이거", "이것", "그거", "그것"]
        if any(trigger in q for trigger in PRONOUN_TRIGGERS):
            all_content = " ".join(m["content"] for m in recent if m["role"] == "assistant")
            pn_matches = re.findall(r'\b[A-Z0-9][A-Z0-9\-#\.+]{4,}\b', all_content)
            if pn_matches:
                last_pn = pn_matches[-1]
                for trigger in PRONOUN_TRIGGERS:
                    q = q.replace(trigger, f"part_number='{last_pn}' 제품")
                logger.info(f"대명사 치환: → {last_pn}")

        ctx_section = "\n[직전 업무 대화 맥락 - 후속질문/대명사 해석에 반드시 활용]\n" + "\n".join(lines) + "\n"
    else:
        ctx_section = ""

    # [7] 에러 유형별 retry 전략 힌트 추출
    error_history = state.get("error_history", [])
    last_error = error_history[-1] if error_history else ""
    retry_info = get_retry_strategy(last_error) if last_error else {}
    if retry_info.get("hint"):
        ctx_section += f"\n[재시도 전략: {retry_info['strategy']}]\n{retry_info['hint']}\n"

    # [11] RAG 병렬 실행
    synonym_hint = state.get("synonym_hint", "")
    rag_section = build_rag_section_parallel(q, synonym_hint, last_error)

    # 전체 스키마 항상 사용
    active_schema = schema_ctx

    resp = (prompt | llm | StrOutputParser()).invoke({
        "q": q, "schema": active_schema,
        "min_d": data_stats.get("min_date"), "max_d": data_stats.get("max_date"),
        "errors": error_history,
        "ctx_section": ctx_section,
        "rag": rag_section
    })
    sql = clean_sql(resp)
    logger.info(f"생성된 SQL:\n{sql}")
    return {"sql_query": sql}






# ==========================================
# [7] 에러 유형별 Retry 전략
# ==========================================
def get_retry_strategy(error_msg: str) -> dict:
    """에러 메시지 → 재시도 전략 딕셔너리 반환"""
    err_lower = error_msg.lower()

    if "does not exist" in err_lower and "column" in err_lower:
        col_match = re.search(r'column "?(\w+)"?', error_msg, re.IGNORECASE)
        missing = col_match.group(1) if col_match else "unknown"
        found_in = [t for t, cols in COLUMN_MAP.items()
                    if missing.lower() in [c.lower() for c in cols]]
        hint = f"'{missing}' 컬럼은 {found_in[0] if found_in else '알 수 없는'} 테이블 소속."
        if found_in:
            hint += f" JOIN {found_in[0]} 후 {found_in[0]}.{missing} 로 참조하세요."
        return {"strategy": "column_missing", "hint": hint}

    if "relation" in err_lower and "does not exist" in err_lower:
        tbl_match = re.search(r'relation "?(\w+)"?', error_msg, re.IGNORECASE)
        missing = tbl_match.group(1) if tbl_match else "unknown"
        return {"strategy": "table_missing",
                "hint": f"테이블 '{missing}' 없음. 유효 테이블: {list(COLUMN_MAP.keys())}"}

    if "syntax error" in err_lower:
        return {"strategy": "syntax",
                "hint": ("SQL 단순화: TO_DATE/DATE_TRUNC 중첩 금지. "
                         "EXTRACT(YEAR FROM col)=연도 사용. "
                         "복잡한 서브쿼리는 CTE(WITH절)로 분리.")}

    if "timeout" in err_lower or "canceling" in err_lower:
        return {"strategy": "timeout",
                "hint": "타임아웃: LIMIT 10으로 축소, WHERE에 날짜 범위 추가, CTE로 분리."}

    if "group by" in err_lower or "aggregate" in err_lower:
        return {"strategy": "logic",
                "hint": "GROUP BY 오류: SELECT의 모든 비집계 컬럼을 GROUP BY에 포함하세요."}

    return {"strategy": "unknown", "hint": error_msg[:300]}




# ==========================================
# [11] RAG 병렬화
# ==========================================
_rag_executor = ThreadPoolExecutor(max_workers=6)

def build_rag_section_parallel(question: str, synonym_hint: str = "", error_msg: str = "") -> str:
    """6종 RAG 병렬 실행 후 섹션 문자열 반환"""
    def run(fn, *args):
        try:
            return fn(*args)
        except Exception:
            return ""

    futures = {
        "fewshot": _rag_executor.submit(run, rag_retrieve_fewshot, question),
        "synonym": _rag_executor.submit(run, rag_retrieve_synonyms, question),
        "bizterm": _rag_executor.submit(run, rag_retrieve_bizterm, question),
        "schema":  _rag_executor.submit(run, rag_retrieve_schema,  question),
        "error":   _rag_executor.submit(run, rag_retrieve_error_hint, error_msg) if error_msg else None,
        "keyword": _rag_executor.submit(run, rag_retrieve_keyword_intent, question),
    }

    results = {}
    for key, fut in futures.items():
        if fut is None:
            results[key] = ""
            continue
        try:
            results[key] = fut.result(timeout=3.0)
        except Exception:
            results[key] = ""
            logger.warning(f"RAG 병렬 타임아웃: {key}")

    section = ""
    if results.get("fewshot"):
        section += f"\n[유사 질문-SQL 예시 (참고용)]\n{results['fewshot']}"
    if synonym_hint or results.get("synonym"):
        section += f"\n[동의어 정보]\n{synonym_hint or results['synonym']}"
    if results.get("bizterm"):
        section += f"\n[비즈니스 용어 정의]\n{results['bizterm']}"
    if results.get("schema"):
        section += f"\n[관련 테이블 스키마]\n{results['schema']}"
    if results.get("error"):
        section += f"\n[에러 해결 힌트]\n{results['error']}"
    if results.get("keyword"):
        section += f"\n[질문 의도 힌트]\n{results['keyword']}"
    return section
  
  
  
  
  def clean_sql(raw: str) -> str:
    """LLM 출력에서 순수 SQL만 추출하는 강화된 클리너"""
    # 1) ANSI 터미널 이스케이프 코드 제거 (←[4m, ←[0m 등)
    raw = re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', raw)
    raw = re.sub(r'\033\[[0-9;]*[mGKHF]', '', raw)
    # 화살표 형태로 깨진 이스케이프도 제거
    raw = re.sub(r'←\[[0-9;]*[mGKHF]', '', raw)

    # 2) 마크다운 코드블록(```sql ... ```) 내의 쿼리만 안전하게 추출
    match = re.search(r'```(?:sql)?\s*(.*?)\s*```', raw, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        # 마크다운 없이 텍스트로만 온 경우, 앞뒤 백틱(```)만 제거
        sql = re.sub(r'^```|```$', '', raw.strip(), flags=re.MULTILINE).strip()

    # 3) 세미콜론 이후 두 번째 구문 및 불필요한 텍스트 제거
    sql = sql.split(';')[0].strip()

    logger.debug(f"clean_sql 결과:\n{sql}")
    return sql
