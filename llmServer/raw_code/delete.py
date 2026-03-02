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
