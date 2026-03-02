# ==========================================
# 🧠 RAG 컬렉션 이름
# ==========================================
COLL_FEWSHOT   = "fewshot_sql"      # 질문-SQL 예시 쌍
COLL_SYNONYM   = "synonym_store"    # 동의어/업체명
COLL_BIZTERM   = "bizterm_store"    # 비즈니스 용어
COLL_SCHEMA    = "table_schema"     # 테이블-컬럼 Rich 문장
COLL_ERROR     = "error_pattern"    # 에러→해결책 패턴
COLL_KEYWORD   = "keyword_intent"   # 키워드→의도 매핑

# ※ Few-shot/동의어/용어 데이터는 rag_builder.ipynb에서 관리합니다


# [#8] 쿼리 결과 최대 건수 제한
QUERY_RESULT_LIMIT = 10_000

# [#7] 최대 SQL 재시도 횟수
MAX_RETRY_COUNT = 2

# [기능] 파이썬 내장 frozenset 해시 테이블을 활용하여 O(1) 탐색 속도 보장 및 대용량 호출 시 메모리 최적화
# [기능] part_number를 공유하는 모든 테이블 간의 10가지 교차 조합 및 제조사/고객사 외래키 매핑 완비
VALID_JOINS = {
    # part_number 기준 JOIN 조합
    frozenset(['products', 'current_products']): 'part_number',
    frozenset(['products', 'initial_inventory']): 'part_number',
    frozenset(['products', 'purchase_orders']): 'part_number',
    frozenset(['products', 'sales_orders']): 'part_number',
    frozenset(['current_products', 'initial_inventory']): 'part_number',
    frozenset(['current_products', 'purchase_orders']): 'part_number',
    frozenset(['current_products', 'sales_orders']): 'part_number',
    frozenset(['initial_inventory', 'purchase_orders']): 'part_number',
    frozenset(['initial_inventory', 'sales_orders']): 'part_number',
    frozenset(['purchase_orders', 'sales_orders']): 'part_number',

    # 별도 외래키 기준 JOIN
    frozenset(['purchase_orders', 'manufacturers']): 'manufacturer_id',
    frozenset(['sales_orders', 'vendors']): 'vendor_id',
}

# ==========================================
# 1. 리소스 로드 및 지능형 스키마 추출
# ==========================================
@st.cache_resource
def get_resources():
    os.system('pkill -f cloudflared')
    time.sleep(1)
    if not os.path.exists('./cloudflared'):
        os.system('wget -q -O ./cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64')
        os.system('chmod +x ./cloudflared')
    subprocess.Popen(['./cloudflared', 'access', 'tcp', '--hostname', CLOUDFLARE_URL, '--url', 'tcp://127.0.0.1:5433'])
    time.sleep(4)

    db, engine, entity_cache, data_stats, schema_ctx, column_map = None, None, {"manufacturers": [], "vendors": []}, {}, "", {}
    try:
        # ✅ [#5] 커넥션 풀 설정 추가
        engine = create_engine(
            DB_URL,
            connect_args={'connect_timeout': 10},
            pool_size=10,           # 기본 유지 커넥션 수
            max_overflow=20,        # 풀 초과 시 추가 허용 커넥션
            pool_timeout=30,        # 커넥션 대기 최대 시간(초)
            pool_recycle=1800,      # 30분마다 커넥션 재생성 (커넥션 좀비 방지)
            pool_pre_ping=True      # 끊긴 커넥션 자동 감지 및 재연결
        )

        insp = inspect(engine)
        with engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {DB_SCHEMA}"))
            m_rows = conn.execute(text("SELECT name FROM manufacturers LIMIT 1000")).fetchall()
            v_rows = conn.execute(text("SELECT vendor_name FROM vendors LIMIT 1000")).fetchall()
            entity_cache = {"manufacturers": [r[0] for r in m_rows], "vendors": [r[0] for r in v_rows]}
            d_info = conn.execute(text("SELECT MIN(sale_date), MAX(sale_date) FROM sales_orders")).fetchone()
            data_stats = {"min_date": str(d_info[0]), "max_date": str(d_info[1])}

        column_map = {}
        for table in insp.get_table_names(schema=DB_SCHEMA):
            cols = [c['name'] for c in insp.get_columns(table, schema=DB_SCHEMA)]
            column_map[table] = cols
            schema_ctx += f"\n- {table}: {BUSINESS_LOGIC.get(table, '')}\n  Cols: "
            schema_ctx += ", ".join(cols)

        db = SQLDatabase(engine, schema=DB_SCHEMA, sample_rows_in_table_info=0)
        logger.info("DB 리소스 로드 성공")
    except Exception as e:
        # ✅ [#4] print → logger.exception (스택 트레이스 포함)
        logger.exception("리소스 로드 실패")

    # ✅ [수정3] ChatOllama → ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY,
    )


    # ==========================================
    # RAG: 구글드라이브에서 로드 (rag_builder.ipynb에서 미리 구축)
    # ==========================================
    rag_colls = {"fewshot": None, "synonym": None, "bizterm": None, "entity": None, "schema": None, "error": None, "keyword": None}
    try:
        if not os.path.exists(DRIVE_CHROMA_PATH):
            logger.warning("RAG 드라이브 경로 없음. rag_builder.ipynb를 먼저 실행하세요.")
            raise FileNotFoundError(f"드라이브 경로 없음: {DRIVE_CHROMA_PATH}")

        # 드라이브 → 로컬 복사 (IO 속도 개선)
        if os.path.exists(LOCAL_CHROMA_PATH):
            shutil.rmtree(LOCAL_CHROMA_PATH)
        shutil.copytree(DRIVE_CHROMA_PATH, LOCAL_CHROMA_PATH)

        chroma_client = chromadb.PersistentClient(path=LOCAL_CHROMA_PATH)
        emb = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

        def safe_get(name):
            try:
                return chroma_client.get_collection(name, embedding_function=emb)
            except Exception:
                logger.warning(f"컬렉션 없음 (무시): {name}")
                return None

        rag_colls = {
            "fewshot":  safe_get(COLL_FEWSHOT),
            "synonym":  safe_get(COLL_SYNONYM),
            "bizterm":  safe_get(COLL_BIZTERM),
            "entity":   safe_get("entity_store"),
            "schema":   safe_get(COLL_SCHEMA),
            "error":    safe_get(COLL_ERROR),
            "keyword":  safe_get(COLL_KEYWORD),
        }
        counts = {k: v.count() for k, v in rag_colls.items()}
        logger.info(f"RAG 로드 완료: {counts}")

    except Exception:
        logger.exception("RAG 로드 실패 → RAG 없이 실행됩니다 (rag_builder.ipynb 먼저 실행 필요)")

    return db, llm, entity_cache, engine, rag_colls, data_stats, schema_ctx, column_map

db, llm, entity_cache, engine, rag_colls, data_stats, schema_ctx, COLUMN_MAP = get_resources()

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
    query_plan: Dict           # 구조화된 쿼리 계획 JSON

    # ── [3] Dynamic Schema ────────────────────────────
    selected_schema: str       # 선택된 테이블/컬럼 스키마

    # ── [4] Static Validator ──────────────────────────
    validation_errors: List[str]
    retry_strategy: str        # column_missing/table_missing/syntax/timeout/logic

    # ── [5] Result Validator ──────────────────────────
    result_anomalies: List[str]

    # ── [8] 구조화 메모리 ──────────────────────────────
    structured_memory: Dict    # last_metric/last_product/last_date_range 등

    # ── [9] 캐시 ──────────────────────────────────────
    cache_hit: bool
    cache_key: str

    # ── [10] Explainability ───────────────────────────
    explain_meta: Dict         # sql_used/filters_applied/aggregations 등


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
        r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)',
        re.IGNORECASE
    )
    for m in table_pattern.finditer(sql):
        tbl, alias = m.group(1).lower(), m.group(2).lower()
        alias_map[alias] = tbl
        alias_map[tbl] = tbl  # 별칭 없이 테이블명 직접 사용도 처리

    if not alias_map:
        return True, ""

    # alias.column 패턴 추출
    col_ref_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.(\w+)\b')
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
            found_in = [t for t, cols in COLUMN_MAP.items()
                        if col in [c.lower() for c in cols]]
            hint = f"'{col}'은 '{actual_table}'에 없음"
            if found_in:
                hint += f" → '{found_in[0]}' 테이블 소속. JOIN 필요"
            errors.append(hint)

    if errors:
        err_msg = "컬럼 소속 오류: " + " | ".join(errors)
        return False, err_msg

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
    if re.search(r'SELECT\s+\*', sql_upper):
        errors.append("SELECT * 금지. 필요한 컬럼을 명시하세요.")
        strategy = "syntax"

    # 2. GROUP BY 누락 검사 (집계함수 + 비집계 컬럼 혼합)
    has_agg = bool(re.search(r'\b(SUM|AVG|COUNT|MAX|MIN)\s*\(', sql_upper))
    has_grp = bool(re.search(r'\bGROUP\s+BY\b', sql_upper))
    has_win = bool(re.search(r'\bOVER\s*\(', sql_upper))
    if has_agg and not has_grp and not has_win:
        sel_m = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if sel_m:
            cleaned = re.sub(r'(SUM|AVG|COUNT|MAX|MIN)\s*\([^)]+\)', '', sel_m.group(1), flags=re.IGNORECASE)
            non_agg = [c.strip() for c in cleaned.split(',')
                       if c.strip() and c.strip() not in ('', '*')
                       and not c.strip().upper().startswith('AS')]
            if non_agg:
                errors.append(f"GROUP BY 누락: 비집계 컬럼 존재. GROUP BY 추가 필요.")
                strategy = "logic"

    # 3. Cartesian Product 감지 (JOIN ON 조건 부족)
    join_cnt = len(re.findall(r'\bJOIN\b', sql_upper))
    on_cnt   = len(re.findall(r'\bON\b|\bUSING\b', sql_upper))
    if join_cnt > 0 and on_cnt < join_cnt:
        errors.append(f"Cartesian Product 위험: JOIN {join_cnt}개, ON {on_cnt}개. ON 조건 추가 필요.")
        strategy = "logic"

    # 4. 존재하지 않는 테이블 참조
    sql_clean = re.sub(r'EXTRACT\s*\([^)]+\)', 'EXTRACT_PLACEHOLDER', sql, flags=re.IGNORECASE)

    # [기능] WITH 절(CTE)에서 생성된 가상 테이블 이름을 정규식으로 추출
    cte_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\(', sql_clean, re.IGNORECASE)

    ref_tables = re.findall(r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)', sql_clean, re.IGNORECASE)
    skip_aliases = {'_sub', 'sr', 'cum', 'cte', 'sub', 't', 'a', 'b', 'extract_placeholder'}

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
        r'JOIN\s+[a-zA-Z_][a-zA-Z0-9_]*\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)',
        sql, re.IGNORECASE
    )
    for alias in join_aliases:
        # [기능] ON, USING 등의 SQL 예약어는 별칭이 아니므로 검사에서 제외
        if alias.upper() in ('ON', 'USING'):
            continue

        usage = re.findall(rf'\b{re.escape(alias)}\.[a-zA-Z_]', sql, re.IGNORECASE)
        if not usage:
            errors.append(f"불필요한 JOIN: '{alias}' JOIN 후 컬럼 미사용.")

    # 7. 테이블 JOIN 키 매핑 정적 검증 (LLM 환각 방지)
    # [기능] 사전 정의된 VALID_JOINS 규칙을 통해 잘못된 컬럼 간의 JOIN을 원천 차단
    # [메모리 최적화] 대용량 쿼리 문자열 처리 시 리스트 전체를 반환하는 findall 대신
    # 제너레이터 방식인 finditer를 사용하여 메모리 점유율을 최소화
    alias_map = {}
    for m in re.finditer(r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)', sql, re.IGNORECASE):
        tbl, alias = m.group(1).lower(), m.group(2).lower()
        if alias.upper() not in ('ON', 'USING', 'WHERE', 'GROUP', 'ORDER', 'LEFT', 'RIGHT', 'INNER'):
            alias_map[alias] = tbl
            alias_map[tbl] = tbl

    # ON 절 검증 시에도 메모리 최적화를 위해 finditer 적용
    for on_clause in re.finditer(r'ON\s+([a-zA-Z_]+)\.([a-zA-Z_]+)\s*=\s*([a-zA-Z_]+)\.([a-zA-Z_]+)', sql, re.IGNORECASE):
        a1, c1, a2, c2 = on_clause.groups()
        t1, t2 = alias_map.get(a1.lower()), alias_map.get(a2.lower())

        if t1 and t2 and t1 != t2:
            pair = frozenset([t1, t2])
            expected_key = VALID_JOINS.get(pair)

            # 사전에 정의된 관계일 경우, 양쪽 컬럼이 모두 지정된 키와 일치하는지 확인
            if expected_key:
                if c1.lower() != expected_key or c2.lower() != expected_key:
                    errors.append(f"잘못된 JOIN: '{t1}'과 '{t2}'는 '{expected_key}' 컬럼으로 연결해야 합니다.")
                    strategy = "logic"

    if errors:
        return False, " | ".join(errors), strategy
    return True, "", "none"



# ==========================================
# [8] 구조화 대화 메모리
# ==========================================
def update_structured_memory(memory: dict, question: str,
                              df, plan: dict, sql: str) -> dict:
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

    updated["last_sql"]     = sql
    updated["last_filters"] = filters
    return updated


# ==========================================
# [9] 질문 캐싱
# ==========================================
CACHE_TTL_MINUTES = 30
CACHE_MAX_SIZE    = 50

def _normalize_question(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r'\s+', ' ', q)
    q = re.sub(r'\b(\d{2})년\b', lambda m: f"20{m.group(1)}년", q)
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
    cache[key] = {"result": result, "cached_at": datetime.now().isoformat(), "question": question}
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


# ==========================================
# [10] Explainability
# ==========================================
def build_explain_meta(sql: str, df, plan: dict) -> dict:
    """실행 결과에서 설명 메타 추출"""
    tables_used = list(set(re.findall(
        r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)', sql, re.IGNORECASE
    )))
    agg_matches = re.findall(r'(SUM|AVG|COUNT|MAX|MIN)\s*\(([^)]+)\)', sql, re.IGNORECASE)
    aggregations = [f"{fn}({col.strip()})" for fn, col in agg_matches]

    filters_applied = []
    where_m = re.search(r'WHERE\s+(.*?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)',
                         sql, re.IGNORECASE | re.DOTALL)
    if where_m:
        raw_where = where_m.group(1).strip()
        filters_applied = [f.strip() for f in
                           re.split(r'\bAND\b|\bOR\b', raw_where, flags=re.IGNORECASE)
                           if f.strip()]

    return {
        "sql_used":        sql,
        "tables_used":     tables_used,
        "aggregations":    aggregations,
        "filters_applied": filters_applied[:5],
        "group_by":        (plan or {}).get("group_by", "none"),
        "row_count":       len(df) if df is not None else 0,
        "intent_summary":  (plan or {}).get("intent_summary", ""),
    }

EXPLAIN_TRIGGERS = ["어떻게 계산", "왜 이 값", "어떻게 나온", "설명해줘", "근거", "어떻게 구한"]

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


# 자동 시각화
# ==========================================
# [5] Result Validation 노드
# ==========================================
def result_validate_node(state: AgentState) -> dict:
    """DB 실행 성공 후 결과 데이터 sanity check
    - 0건: 재시도 X, answer_node에서 '데이터 없음'으로 안내
    - 음수 매출 / 비정상 이상값: 재시도 O (SQL 로직 오류 가능성)
    """
    df   = state.get("df")
    plan = state.get("query_plan", {})
    anomalies = []

    # 0건은 재시도 하지 않음 - answer_node가 "데이터 없음"으로 처리
    if df is None or len(df) == 0:
        return {"result_anomalies": []}

    # NULL 비율 과다 (80% 이상으로 기준 강화 - 50%는 너무 민감)
    for col in df.columns:
        null_ratio = df[col].isna().sum() / len(df)
        if null_ratio > 0.8:
            anomalies.append(f"'{col}' NULL {null_ratio:.0%} 초과.")

    # 음수 매출/수익 (비즈니스 규칙 위반 - 재시도 가치 있음)
    for col in df.columns:
        if any(k in col.lower() for k in ['revenue','price','cost','profit','amount','매출','수익']):
            if pd.api.types.is_numeric_dtype(df[col]):
                neg = (df[col] < 0).sum()
                if neg > 0:
                    anomalies.append(f"'{col}' 음수값 {neg}건 (비즈니스 규칙 위반).")

    # 비정상 이상값 (평균의 10000배 초과로 기준 완화)
    for col in df.select_dtypes(include='number').columns:
        mean_v = df[col].mean()
        if mean_v > 0:
            max_v = df[col].max()
            if max_v > mean_v * 10000:
                anomalies.append(f"'{col}' 최대값({max_v:,.0f}) 이상 감지.")

    if anomalies:
        logger.warning(f"Result Anomaly: {anomalies}")
        return {
            "result_anomalies": anomalies,
            "db_result": f"Error: 결과 이상 감지 - {' | '.join(anomalies)}",
            "error_history": state.get("error_history", []) + anomalies,
            "retry_count": state.get("retry_count", 0) + 1,
        }
    return {"result_anomalies": []}


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
    "그래프", "차트", "그려", "시각화", "plot", "chart", "graph",
    "막대", "선그래프", "파이", "도표", "그림", "보여줘", "표시"
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
        ctx_lines = [f"{'사용자' if m['role']=='user' else 'AI'}: {m['content'][:100]}"
                     for m in work_ctx[-4:]]
        ctx_str = "\n".join(ctx_lines) if ctx_lines else "없음"
        prompt = PromptTemplate.from_template("""당신은 전자부품 수입 유통 전문 테크니컬 세일즈 AI입니다.
전자부품 스펙, 대체품, 납기, 호환성, 기술 문의에 전문적으로 답변하세요.

[직전 업무 대화 맥락]
{ctx}

[질문]
{q}

[답변 규칙]
- 확실하지 않은 스펙은 "데이터시트 확인 필요"로 명시
- 대체품 추천 시 반드시 호환성 주의사항 포함
- 간결하고 전문적으로 답변""")
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
    prompt = PromptTemplate.from_template("""당신은 전자부품 재고 데이터 분석가입니다.
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

답변:""")

    row_count = len(df)
    # [기능] 데이터가 있음에도 헛소리하는 것을 막기 위해 meta 정보에 강한 어조 추가
    meta_info = f"현재 총 {row_count}행의 데이터가 정상 조회되었습니다. 이 데이터를 기반으로 즉시 답변하세요. 데이터 부재를 핑계로 답변을 거부하지 마세요."

    try:
        ans = (prompt | llm | StrOutputParser()).invoke({
            "q": state["question"],
            "d": df.head(10).to_string(),
            "meta": meta_info
        })
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
workflow.add_node("refine",          entity_linking_node)
workflow.add_node("router",          router_node)
workflow.add_node("sql_gen",         generate_sql_node)
workflow.add_node("db_exec",         execute_db_node)
workflow.add_node("result_validate", result_validate_node)
workflow.add_node("visual",          visualize_node)
workflow.add_node("answer",          answer_node)

workflow.set_entry_point("refine")
workflow.add_edge("refine", "router")

def route_by_intent(state):
    intent = state.get("intent", "INVENTORY")
    if intent in ("CHIT_CHAT", "TECH_SALES"):
        return "answer"
    return "sql_gen"  # INVENTORY → 바로 sql_gen

workflow.add_conditional_edges(
    "router",
    route_by_intent,
    {"answer": "answer", "sql_gen": "sql_gen"}
)

# sql_gen → db_exec (재시도 포함)
workflow.add_edge("sql_gen", "db_exec")
workflow.add_conditional_edges(
    "db_exec", should_retry,
    {"retry": "sql_gen", "success": "result_validate"}
)

# result_validate → 이상없으면 visual, 이상있으면 sql_gen 재시도
workflow.add_conditional_edges(
    "result_validate", should_retry_result,
    {"retry": "sql_gen", "visual": "visual"}
)

workflow.add_edge("visual", "answer")
workflow.add_edge("answer", END)
app_agent = workflow.compile()

# ==========================================
# 4. 세션 히스토리 영속화 (PostgreSQL)  [#9]
# ==========================================
def load_session_history(session_id: str) -> list:
    """DB에서 세션 대화 이력 불러오기"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """))
            conn.commit()
            rows = conn.execute(text(
                "SELECT role, content FROM chat_sessions WHERE session_id=:sid ORDER BY created_at"
            ), {"sid": session_id}).fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]
    except Exception:
        logger.exception("세션 이력 로드 실패")
        return []

def save_message(session_id: str, role: str, content: str):
    """DB에 대화 메시지 저장"""
    try:
        with engine.connect() as conn:
            conn.execute(text(
                "INSERT INTO chat_sessions (session_id, role, content) VALUES (:sid, :role, :content)"
            ), {"sid": session_id, "role": role, "content": content})
            conn.commit()
    except Exception:
        logger.exception("메시지 저장 실패")