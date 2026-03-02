# ==========================================
# 2. 에이전트 노드 정의 (자가 치유 포함)
# ==========================================
class AgentState(TypedDict, total=False):
    # ── 기존 ──────────────────────────────────────────
    question: str
    refined_question: str
    synonym_hint: str
    intent: str
    sql_query: str
    db_result: any
    df: pd.DataFrame
    chart_info: Dict
    error_history: List[str]
    retry_count: int

    # ── [1] Query Planner ─────────────────────────────
    query_plan: Dict  # 구조화된 쿼리 계획 JSON

    # ── [3] Dynamic Schema ────────────────────────────
    selected_schema: str  # 선택된 테이블/컬럼 스키마

    # ── [4] Static Validator ──────────────────────────
    validation_errors: List[str]
    retry_strategy: str  # column_missing/table_missing/syntax/timeout/logic

    # ── [5] Result Validator ──────────────────────────
    result_anomalies: List[str]

    # ── [8] 구조화 메모리 ──────────────────────────────
    structured_memory: Dict  # last_metric/last_product/last_date_range 등

    # ── [9] 캐시 ──────────────────────────────────────
    cache_hit: bool
    cache_key: str

    # ── [10] Explainability ───────────────────────────
    explain_meta: Dict  # sql_used/filters_applied/aggregations 등


# ==========================================
# [8] 구조화 대화 메모리
# ==========================================
def update_structured_memory(
    memory: dict, question: str, df, plan: dict, sql: str
) -> dict:
    """쿼리 결과에서 구조화 메모리 업데이트"""
    updated = memory.copy() if memory else {}
    q_lower = question.lower()

    # last_metric
    if any(k in q_lower for k in ["매출", "revenue", "판매금"]):
        updated["last_metric"] = "매출액"
    elif any(k in q_lower for k in ["매입", "purchase", "구매"]):
        updated["last_metric"] = "매입액"
    elif any(k in q_lower for k in ["수익", "이익", "profit"]):
        updated["last_metric"] = "수익"
    elif any(k in q_lower for k in ["재고", "stock", "수량"]):
        updated["last_metric"] = "재고수량"

    # last_product
    if df is not None and "part_number" in df.columns and len(df) > 0:
        updated["last_product"] = str(df.iloc[0]["part_number"])

    # last_date_range
    filters = plan.get("filters", {}) if plan else {}
    date_range = {}
    if filters.get("year"):
        date_range["year"] = filters["year"]
    if filters.get("quarter"):
        date_range["quarter"] = filters["quarter"]
    if date_range:
        updated["last_date_range"] = date_range

    # last_vendor / last_manufacturer / last_category
    if df is not None:
        if "vendor_name" in df.columns and len(df) > 0:
            updated["last_vendor"] = str(df.iloc[0]["vendor_name"])
        if "name" in df.columns and len(df) > 0:
            updated["last_manufacturer"] = str(df.iloc[0]["name"])

    if filters.get("category"):
        updated["last_category"] = filters["category"]

    updated["last_sql"] = sql
    updated["last_filters"] = filters
    return updated


# ==========================================
# [9] 질문 캐싱
# ==========================================
CACHE_TTL_MINUTES = 30
CACHE_MAX_SIZE = 50


def _normalize_question(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r"\s+", " ", q)
    q = re.sub(r"\b(\d{2})년\b", lambda m: f"20{m.group(1)}년", q)
    return q


def cache_get(question: str) -> dict | None:
    cache = st.session_state.get("query_cache", {})
    key = hashlib.md5(_normalize_question(question).encode()).hexdigest()
    if key in cache:
        entry = cache[key]
        cached_at = datetime.fromisoformat(entry["cached_at"])
        if datetime.now() - cached_at < timedelta(minutes=CACHE_TTL_MINUTES):
            logger.info(f"캐시 HIT: {question[:40]}")
            return entry["result"]
        else:
            del cache[key]
    return None


def cache_save(question: str, result: dict):
    if "query_cache" not in st.session_state:
        st.session_state.query_cache = {}
    cache = st.session_state.query_cache
    key = hashlib.md5(_normalize_question(question).encode()).hexdigest()
    cache[key] = {
        "result": result,
        "cached_at": datetime.now().isoformat(),
        "question": question,
    }
    # 크기 초과 시 가장 오래된 것 삭제
    if len(cache) > CACHE_MAX_SIZE:
        oldest = min(cache, key=lambda k: cache[k]["cached_at"])
        del cache[oldest]


def cache_invalidate(pattern: str = ""):
    """패턴 포함 캐시 무효화 (pattern="" 이면 전체)"""
    cache = st.session_state.get("query_cache", {})
    if not pattern:
        st.session_state.query_cache = {}
        logger.info("캐시 전체 초기화")
        return
    to_del = [k for k, v in cache.items() if pattern in v.get("question", "")]
    for k in to_del:
        del cache[k]
    logger.info(f"캐시 무효화 {len(to_del)}개 ({pattern})")


EXPLAIN_TRIGGERS = [
    "어떻게 계산",
    "왜 이 값",
    "어떻게 나온",
    "설명해줘",
    "근거",
    "어떻게 구한",
]


def should_retry_result(state: AgentState) -> str:
    if state.get("result_anomalies") and state.get("retry_count", 0) < MAX_RETRY_COUNT:
        return "retry"
    return "visual"


def sanitize_chart_info(info: dict, df_columns: list) -> dict:
    """LLM이 반환한 chart_info를 안전하게 정규화"""
    # x, y가 리스트로 반환된 경우 첫 번째 원소만 사용
    x = info.get("x", "")
    y = info.get("y", "")
    if isinstance(x, list):
        x = x[0] if x else ""
    if isinstance(y, list):
        y = y[0] if y else ""
    # 문자열 보장
    x = str(x).strip()
    y = str(y).strip()
    # 실제 컬럼명과 다를 경우 타입 기반 자동 추론
    if x not in df_columns or y not in df_columns:
        num_cols = [c for c in df_columns if c not in (x,)]
        str_cols = [c for c in df_columns]
        # 첫 번째 컬럼을 x, 첫 번째 숫자형 컬럼을 y로 자동 할당
        x = df_columns[0] if df_columns else x
        y = num_cols[0] if num_cols else (df_columns[1] if len(df_columns) > 1 else y)
        logger.warning(f"차트 컬럼 자동 보정: x={x}, y={y}")
    return {"type": info.get("type", "none"), "x": x, "y": y}


# 차트 요청 키워드
CHART_KEYWORDS = [
    "그래프",
    "차트",
    "그려",
    "시각화",
    "plot",
    "chart",
    "graph",
    "막대",
    "선그래프",
    "파이",
    "도표",
    "그림",
    "보여줘",
    "표시",
]


def is_chart_requested(question: str) -> bool:
    return any(kw in question for kw in CHART_KEYWORDS)


def infer_chart_type(question: str) -> str:
    """질문 키워드로 차트 타입 직접 결정 - LLM 호출 없음"""
    q = question.lower()
    if any(k in q for k in ["파이", "비율", "점유", "pie"]):
        return "pie"
    if any(k in q for k in ["추이", "변화", "흐름", "트렌드", "선", "line", "시계열"]):
        return "line"
    return "bar"  # 기본값


def infer_chart_columns(df: pd.DataFrame) -> tuple[str, str]:
    """DataFrame 컬럼 타입으로 x/y 자동 결정 - LLM 호출 없음"""
    cols = df.columns.tolist()
    # 숫자형 컬럼 탐지
    num_cols = df.select_dtypes(include="number").columns.tolist()
    str_cols = [c for c in cols if c not in num_cols]

    x = str_cols[0] if str_cols else cols[0]
    y = num_cols[0] if num_cols else (cols[1] if len(cols) > 1 else cols[0])
    return x, y


def visualize_node(state: AgentState):
    # 사용자가 차트를 명시적으로 요청한 경우에만 시각화
    if not is_chart_requested(state.get("question", "")):
        return {"chart_info": {"type": "none"}}
    df = state.get("df")
    if df is None or df.empty or len(df.columns) < 2:
        return {"chart_info": {"type": "none"}}

    # LLM 호출 없이 직접 추론 → 속도 대폭 개선
    chart_type = infer_chart_type(state.get("question", ""))
    x, y = infer_chart_columns(df)
    logger.info(f"차트 자동 추론: type={chart_type}, x={x}, y={y}")
    return {"chart_info": {"type": chart_type, "x": x, "y": y}}


# 최종 답변 생성
def answer_node(state: AgentState):
    if state.get("intent") == "CHIT_CHAT":
        return {"db_result": "__CHIT_CHAT__"}

    if state.get("intent") == "TECH_SALES":
        q = state.get("question", "")
        work_ctx = st.session_state.get("work_context", [])
        ctx_lines = [
            f"{'사용자' if m['role']=='user' else 'AI'}: {m['content'][:100]}"
            for m in work_ctx[-4:]
        ]
        ctx_str = "\n".join(ctx_lines) if ctx_lines else "없음"
        prompt = PromptTemplate.from_template(
            """당신은 전자부품 수입 유통 전문 테크니컬 세일즈 AI입니다.
전자부품 스펙, 대체품, 납기, 호환성, 기술 문의에 전문적으로 답변하세요.

[직전 업무 대화 맥락]
{ctx}

[질문]
{q}

[답변 규칙]
- 확실하지 않은 스펙은 "데이터시트 확인 필요"로 명시
- 대체품 추천 시 반드시 호환성 주의사항 포함
- 간결하고 전문적으로 답변"""
        )
        try:
            ans = (prompt | llm | StrOutputParser()).invoke({"q": q, "ctx": ctx_str})
        except Exception:
            ans = "테크니컬 문의 처리 중 오류가 발생했습니다."
        return {"db_result": ans}

    db_res = state.get("db_result", "")
    if "Error" in db_res:
        return {"db_result": f"❌ 분석 실패: {db_res}"}

    df = state.get("df")
    if df is None or df.empty:
        return {"db_result": "🔍 해당 조건의 데이터가 존재하지 않습니다."}

    # ==========================================
    # [수정] 환각 방지 및 데이터 해석 강화 프롬프트
    # ==========================================
    prompt = PromptTemplate.from_template(
        """당신은 전자부품 재고 데이터 분석가입니다.
아래 제공된 [실제 데이터] 테이블은 DB에서 갓 뽑아온 '진실'입니다.
테이블에 단 한 줄이라도 데이터가 있다면, 정보를 확인할 수 없다는 답변은 '오답'이자 '거짓말'입니다.

[질문]
{q}

[실제 데이터]
{d}

[데이터 메타 정보]
{meta}

[답변 절대 지침] ← 위반 시 업무 태만
1. 데이터 맹신: 테이블에 'IC'라고 적혀 있으면 파나소닉 제품 종류는 'IC'인 것입니다. 데이터가 부족하다고 변명하지 마세요.
2. 부정 답변 금지: "정보가 포함되어 있지 않습니다", "확인할 수 없습니다", "알 수 없습니다" 같은 표현을 절대 사용하지 마세요.
3. 팩트 기반 요약: 테이블의 내용을 그대로 읽어서 2~3문장으로 답변하세요.
4. 마크다운 표 생성 금지: 텍스트로만 설명하세요. 화면에 이미 표가 그려져 있습니다.

[단위 규칙]
- 금액: 원(KRW) 단위, 반올림 정수 표기 (예: 1,200,000,000원)
- 수량: 개 단위 표기

답변:"""
    )

    row_count = len(df)
    # [기능] 데이터가 있음에도 헛소리하는 것을 막기 위해 meta 정보에 강한 어조 추가
    meta_info = f"현재 총 {row_count}행의 데이터가 정상 조회되었습니다. 이 데이터를 기반으로 즉시 답변하세요. 데이터 부재를 핑계로 답변을 거부하지 마세요."

    try:
        ans = (prompt | llm | StrOutputParser()).invoke(
            {"q": state["question"], "d": df.head(10).to_string(), "meta": meta_info}
        )
    except Exception as e:
        ans = f"답변 생성 중 오류가 발생했습니다: {str(e)}"

    return {"db_result": ans}


# ==========================================
# 3. 그래프 조립
# ==========================================
# ✅ [#7] retry_count 기반 이중 재시도 제한
def should_retry(state: AgentState) -> str:
    has_error = "Error" in state.get("db_result", "")
    under_limit = state.get("retry_count", 0) < MAX_RETRY_COUNT
    if has_error and under_limit:
        return "retry"
    return "success"


workflow = StateGraph(AgentState)

# 노드 등록
workflow.add_node("refine", entity_linking_node)
workflow.add_node("router", router_node)
workflow.add_node("sql_gen", generate_sql_node)
workflow.add_node("db_exec", execute_db_node)
workflow.add_node("result_validate", result_validate_node)
workflow.add_node("visual", visualize_node)
workflow.add_node("answer", answer_node)

workflow.set_entry_point("refine")
workflow.add_edge("refine", "router")


def route_by_intent(state):
    intent = state.get("intent", "INVENTORY")
    if intent in ("CHIT_CHAT", "TECH_SALES"):
        return "answer"
    return "sql_gen"  # INVENTORY → 바로 sql_gen


workflow.add_conditional_edges(
    "router", route_by_intent, {"answer": "answer", "sql_gen": "sql_gen"}
)

# sql_gen → db_exec (재시도 포함)
workflow.add_edge("sql_gen", "db_exec")
workflow.add_conditional_edges(
    "db_exec", should_retry, {"retry": "sql_gen", "success": "result_validate"}
)

# result_validate → 이상없으면 visual, 이상있으면 sql_gen 재시도
workflow.add_conditional_edges(
    "result_validate", should_retry_result, {"retry": "sql_gen", "visual": "visual"}
)

workflow.add_edge("visual", "answer")
workflow.add_edge("answer", END)
app_agent = workflow.compile()
