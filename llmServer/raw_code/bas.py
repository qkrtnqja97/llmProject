%%writefile app.py
import streamlit as st
import pandas as pd
import ast, re, os, subprocess, time, shutil, json, hashlib
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import logging
from typing import TypedDict, Optional, Dict, List
from langgraph.graph import StateGraph, END
# ✅ [수정1] ChatOllama → ChatGoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from sqlalchemy import create_engine, text, inspect
from rapidfuzz import process, fuzz
import chromadb
from chromadb.utils import embedding_functions
import sqlglot  # pip install sqlglot

# ==========================================
# 📋 [#4] 로깅 설정 (print → logging)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EnterpriseAI")

# [기능] 차트 한글 깨짐 방지
plt.rcParams['font.family'] = 'NanumBarunGothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Enterprise AI Agent", page_icon="🏢", layout="wide")
st.title("📈 엔터프라이즈 재고 분석 시스템")

# ==========================================
# ⚙️ 시스템 설정값
# ==========================================
CLOUDFLARE_URL = "requests-nerve-largely-started.trycloudflare.com"
DRIVE_CHROMA_PATH = "/content/drive/MyDrive/프로젝트llm/vdata"
LOCAL_CHROMA_PATH = "/content/local_vdata"
DB_URL = "postgresql+psycopg2://name:1234@127.0.0.1:5433/postgres"
DB_SCHEMA = "inventory_mgmt"
EMBED_MODEL = "BAAI/bge-m3"

# ✅ [수정2] Gemini API 키 설정
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

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

# [기능] 비즈니스 메타데이터 정의 (상세 스키마 학습용)
BUSINESS_LOGIC = {
    "products": """[제품 마스터] 회사가 취급하는 300종 전자부품 핵심 정보.
  - part_number: VARCHAR PK. 부품 고유번호 (예: 80-CBR04C...). 다른 테이블과 JOIN 기준.
  - description: VARCHAR. 부품 카테고리 코드 (IC / FET/TR / C_CHIP/CAP / R_CHIP/RES 등).
    ※ 카테고리 코드이며 상세 설명 아님. 정확한 코드값으로만 필터링.
  - std_unit_cost: NUMERIC. 표준 매입 원가. 예산 수립 기준가. 실제 매입단가는 purchase_orders.actual_unit_cost 사용.
  - std_selling_price: NUMERIC. 표준 판매가(시장 고시가). 실제 판매단가는 sales_orders.actual_selling_price 사용.
  ※ 날짜 컬럼 없음 → 날짜 필터 절대 사용 금지.""",

    "manufacturers": """[제조사/공급처] 부품을 공급하는 제조사 마스터. 총 69개사.
  - manufacturer_id: INTEGER PK. 공급처 식별자.
  - name: VARCHAR UNIQUE. 업체명. UNIQUE 제약으로 중복 등록 불가.
    ※ DB에 오타 변형 존재: BROADCO/BROMDCOM/BRPADCOM=BROADCOM, INETL=INTEL, RENASAS=RENESAS 등.
    ※ 특정 제조사 조회 시 IN ('정식명','오타변형') 형태로 처리 권장.
  ※ 날짜 컬럼 없음 → 날짜 필터 절대 사용 금지.""",

    "vendors": """[판매처/고객사] 부품을 구매하는 고객사 마스터. 총 29개사.
  - vendor_id: INTEGER PK. 고객사 식별자.
  - vendor_name: VARCHAR. 고객사명 (Digikey, Mouser, Farnell, RS, TI, ST, ROHM 등).
    ※ 일부 vendor_name에 줄바꿈 문자 포함 가능 (예: SAMSUNG WALSIN). LIKE 검색 시 주의.
  ※ 날짜 컬럼 없음 → 날짜 필터 절대 사용 금지.""",

    "initial_inventory": """[초기 재고 스냅샷] 시스템 운영 시작점(2022-12-31) 기준 재고량.
  - part_number: VARCHAR PK, FK → products.
  - initial_quantity: INTEGER. 기초 재고 수량 (200~800개 사이 부여).
  - stock_date: DATE. 기초 데이터 확정일. 항상 '2022-12-31' 단일값.
  ※ initial_quantity는 오직 initial_inventory 테이블에만 존재. current_products에는 없음.
  ※ 초기재고 vs 현재재고 비교 시: current_products cp JOIN initial_inventory ii ON cp.part_number=ii.part_number
  ※ 날짜 필터 가능하나 stock_date는 단일값이므로 의미 없음.""",

    "current_products": """[실시간 재고 현황] 모든 입출고 이력을 합산한 최종 현재고.
  - part_number: VARCHAR PK, FK → products.
  - description: VARCHAR. 카테고리 코드 (products.description과 동일).
  - current_quantity: INTEGER. 실시간 현재고 = 초기재고 + 총입고 - 총출고.
  - last_updated: DATE. 마지막 재고 계산 일자.
    ※ last_updated는 시스템 내부 갱신 타임스탬프. WHERE 필터 절대 사용 금지.
    ※ current_products에는 initial_quantity 컬럼이 없음. 초기재고는 initial_inventory 테이블에서 JOIN.
    ※ 재고 현황은 항상 전체 조회. 날짜 조건 없이 current_quantity 그대로 사용.""",

    "purchase_orders": """[구매/매입 이력] 제조사로부터 부품을 매입한 거래 내역. 총 13,615건.
  - purchase_id: INTEGER PK. 구매 건별 고유번호.
  - manufacturer_id: INTEGER FK → manufacturers.manufacturer_id. 반드시 JOIN 필요.
  - part_number: VARCHAR FK → products.
  - purchase_quantity: INTEGER. 입고 수량 (500~1,500개 대량 입고 단위).
  - purchase_date: DATE. 입고 일자. 매월 1일·15일 배치 발주 반영.
    ※ 날짜 필터 가능. 형식: 'YYYY-MM-DD'. DATE_TRUNC/EXTRACT 사용.
  - actual_unit_cost: NUMERIC. 실제 매입단가 (시점별 원가 추적용).
    ※ 매입 금액 계산: purchase_quantity * actual_unit_cost.""",

    "sales_orders": """[판매/매출 이력] 고객사에 부품을 판매한 거래 내역. 총 39,572건.
  - order_id: INTEGER PK. 판매 건별 고유번호.
  - vendor_id: INTEGER FK → vendors.vendor_id. 반드시 JOIN 필요.
  - part_number: VARCHAR FK → products.
  - sale_quantity: INTEGER. 출고 수량 (20~150개 분할 출고 단위).
  - sale_date: DATE. 출고 일자. 매주 수요일·금요일 정기 납품 반영.
    ※ 날짜 필터 가능. 형식: 'YYYY-MM-DD'. DATE_TRUNC/EXTRACT 사용.
    ※ 데이터 범위: 2023-01-04 ~ 2025-12-31.
  - actual_selling_price: NUMERIC. 실제 판매단가 (거래처별 실거래가 추적용).
    ※ 매출 금액 계산: sale_quantity * actual_selling_price.
    ※ 수익(총이익) 계산: sale_quantity * (actual_selling_price - products.std_unit_cost).
    ※ vendor_name으로 필터 시 반드시 vendors JOIN 후 vendor_name 조건 사용."""
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


def inject_memory_to_question(question: str, memory: dict) -> str:
    """구조화 메모리로 대명사/생략 표현 자동 보완"""
    if not memory:
        return question
    q = question
    PRONOUN_MAP = {
        "이 제품": "last_product", "해당 제품": "last_product", "그 제품": "last_product",
        "이 고객사": "last_vendor", "해당 고객사": "last_vendor",
        "이 제조사": "last_manufacturer", "해당 제조사": "last_manufacturer",
    }
    for pronoun, key in PRONOUN_MAP.items():
        if pronoun in q and memory.get(key):
            q = q.replace(pronoun, f"'{memory[key]}'")
    if "같은 기간" in q and memory.get("last_date_range"):
        q += f" (기간조건: {memory['last_date_range']})"
    return q


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


# ==========================================
# RAG 조회 헬퍼 함수 (리랭킹 강화 버전)
# ==========================================
import hashlib
from datetime import datetime

# ── 리랭커 모델 로드 (앱 시작 시 1회) ────────────────────────
_reranker = None

def _load_reranker():
    """bge-reranker-v2-m3-ko 크로스인코더 모델 로드"""
    global _reranker
    if _reranker is not None:
        return _reranker
    try:
        try:
            from FlagEmbedding import FlagReranker
        except ImportError:
            import subprocess, sys
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "FlagEmbedding"],
                check=True,
            )
            from FlagEmbedding import FlagReranker

        _reranker = FlagReranker(
            "upskyy/bge-reranker-v2-m3-ko",
            use_fp16=True,   # GPU 있으면 fp16, 없으면 자동 fallback
        )
        logger.info("리랭커 로드 완료: upskyy/bge-reranker-v2-m3-ko")
    except Exception:
        logger.exception("리랭커 로드 실패 → 리랭킹 없이 동작")
        _reranker = None
    return _reranker


def _rerank(query: str, docs: list[str], metas: list[dict],
            top_n: int = 3) -> tuple[list[str], list[dict]]:
    """크로스인코더로 (query, doc) 쌍 점수 계산 후 상위 top_n 반환.
    리랭커 미로드 시 원본 그대로 슬라이싱."""
    reranker = _load_reranker()
    if reranker is None or len(docs) == 0:
        return docs[:top_n], metas[:top_n]

    try:
        pairs = [[query, doc] for doc in docs]
        scores = reranker.compute_score(pairs, normalize=True)
        # compute_score가 단일 float 반환할 수 있음
        if isinstance(scores, (int, float)):
            scores = [scores]

        ranked = sorted(
            zip(scores, docs, metas),
            key=lambda x: x[0],
            reverse=True,
        )
        top = ranked[:top_n]
        return [d for _, d, _ in top], [m for _, _, m in top]
    except Exception:
        logger.exception("리랭킹 실패 → 원본 순서 사용")
        return docs[:top_n], metas[:top_n]


def _rerank_with_scores(query: str, docs: list[str], metas: list[dict],
                        top_n: int = 3) -> tuple[list[str], list[dict], list[float]]:
    """리랭킹 + 점수 반환 버전 (임계값 필터링용)"""
    reranker = _load_reranker()
    if reranker is None or len(docs) == 0:
        return docs[:top_n], metas[:top_n], [1.0] * min(top_n, len(docs))

    try:
        pairs = [[query, doc] for doc in docs]
        scores = reranker.compute_score(pairs, normalize=True)
        if isinstance(scores, (int, float)):
            scores = [scores]

        ranked = sorted(
            zip(scores, docs, metas),
            key=lambda x: x[0],
            reverse=True,
        )
        top = ranked[:top_n]
        return (
            [d for _, d, _ in top],
            [m for _, _, m in top],
            [s for s, _, _ in top],
        )
    except Exception:
        logger.exception("리랭킹(점수) 실패 → 원본 순서 사용")
        return docs[:top_n], metas[:top_n], [1.0] * min(top_n, len(docs))


# ── 하이브리드 검색용 BM25 인덱스 (앱 시작 시 1회 구축) ──────
_bm25_index = None
_bm25_docs  = []
_bm25_metas = []


def _build_bm25_index():
    """fewshot 컬렉션 전체를 BM25 인덱스로 구축"""
    global _bm25_index, _bm25_docs, _bm25_metas
    coll = rag_colls.get("fewshot")
    if not coll:
        return
    try:
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            import subprocess, sys
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "rank-bm25"],
                check=True,
            )
            from rank_bm25 import BM25Okapi

        all_data    = coll.get()
        _bm25_docs  = all_data["documents"]
        _bm25_metas = all_data["metadatas"]
        tokenized   = [doc.split() for doc in _bm25_docs]
        _bm25_index = BM25Okapi(tokenized)
        logger.info(f"BM25 인덱스 구축 완료: {len(_bm25_docs)}개")
    except ImportError:
        logger.warning("rank_bm25 미설치 → pip install rank-bm25")
    except Exception:
        logger.exception("BM25 인덱스 구축 실패")


# 시작 시 1회 실행
_build_bm25_index()
# 리랭커도 미리 로드 (첫 쿼리 지연 방지)
_load_reranker()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1) Few-shot 검색 (하이브리드 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_fewshot(question: str, n: int = 3) -> str:
    """하이브리드 검색 (벡터 + BM25) → 리랭킹 → 상위 n개 Few-shot 예시"""
    coll = rag_colls.get("fewshot")
    if not coll:
        return ""
    try:
        total   = coll.count()
        fetch_n = min(n * 5, total)  # 리랭킹용 후보를 넉넉히 확보

        # ── 1단계: 벡터 검색 ──
        vec_res   = coll.query(query_texts=[question], n_results=fetch_n)
        vec_docs  = vec_res["documents"][0]
        vec_metas = vec_res["metadatas"][0]
        vec_dists = vec_res["distances"][0]
        vec_scores = {doc: 1 - dist for doc, dist in zip(vec_docs, vec_dists)}

        # ── 2단계: BM25 키워드 검색 ──
        bm25_scores = {}
        bm25_meta_map = {}
        if _bm25_index is not None:
            tokens    = question.split()
            scores    = _bm25_index.get_scores(tokens)
            top_idx   = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:fetch_n]
            max_score = max(scores) if max(scores) > 0 else 1
            for i in top_idx:
                if scores[i] > 0:
                    bm25_scores[_bm25_docs[i]]   = scores[i] / max_score
                    bm25_meta_map[_bm25_docs[i]]  = _bm25_metas[i]

        # ── 3단계: 1차 점수 병합 (벡터 0.6 + BM25 0.4) ──
        # doc→meta 통합 맵
        doc_meta_map = {}
        for doc, meta in zip(vec_docs, vec_metas):
            doc_meta_map[doc] = meta
        doc_meta_map.update(bm25_meta_map)

        all_docs = set(vec_docs) | set(bm25_scores.keys())
        merged = {}
        for doc in all_docs:
            v = vec_scores.get(doc, 0)
            b = bm25_scores.get(doc, 0)
            merged[doc] = v * 0.6 + b * 0.4

        # 1차 후보: 상위 n*3개 (리랭커 입력용)
        pre_top = sorted(merged, key=merged.get, reverse=True)[:n * 3]
        pre_docs  = pre_top
        pre_metas = [doc_meta_map.get(d, {}) for d in pre_top]

        # ── 4단계: 크로스인코더 리랭킹 ──
        final_docs, final_metas = _rerank(question, pre_docs, pre_metas, top_n=n)

        # ── 5단계: 결과 포맷 ──
        examples = []
        for doc, meta in zip(final_docs, final_metas):
            sql = meta.get("sql", "")
            if sql:
                examples.append(f"Q: {doc}\nSQL: {sql}")

        logger.debug(f"Fewshot 리랭킹 결과: {[d[:30] for d in final_docs]}")
        return "\n---\n".join(examples)

    except Exception:
        logger.exception("Few-shot 하이브리드+리랭킹 실패 → 벡터 폴백")
        try:
            res = coll.query(query_texts=[question], n_results=min(n, coll.count()))
            return "\n---\n".join(
                [f"Q: {d}\nSQL: {m['sql']}"
                 for d, m in zip(res["documents"][0], res["metadatas"][0])]
            )
        except Exception:
            return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2) 동의어 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_synonyms(question: str, n: int = 3) -> str:
    """동의어 감지: 후보 10개 → 리랭킹 → 상위 n개 중 점수 임계값 통과분 반환"""
    coll = rag_colls.get("synonym")
    if not coll:
        return ""
    try:
        fetch_n = min(10, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        # 리랭킹 + 점수
        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score > 0.3:  # 리랭커 정규화 점수 임계값
                hints.append(f"'{doc}' → '{meta['canonical']}' ({meta['type']})")

        return ", ".join(hints) if hints else ""
    except Exception:
        logger.exception("동의어 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3) 비즈니스 용어 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_bizterm(question: str, n: int = 3) -> str:
    """비즈니스 용어: 후보 8개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("bizterm")
    if not coll:
        return ""
    try:
        fetch_n = min(8, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        terms = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score > 0.25:
                terms.append(f"{doc}: {meta['desc']}")

        return "\n".join(terms) if terms else ""
    except Exception:
        logger.exception("비즈니스 용어 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4) 스키마 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_schema(question: str, n: int = 3) -> str:
    """관련 테이블 스키마: 후보 8개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("schema")
    if not coll:
        return ""
    try:
        fetch_n = min(8, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, score in zip(final_docs, final_scores):
            if score > 0.2:
                hints.append(doc)

        return "\n".join(hints) if hints else ""
    except Exception:
        logger.exception("스키마 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5) 에러 패턴 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_error_hint(error_msg: str, n: int = 3) -> str:
    """에러 해결 힌트: 후보 6개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("error")
    if not coll:
        return ""
    try:
        fetch_n = min(6, coll.count())
        res = coll.query(query_texts=[error_msg], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            error_msg, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, score in zip(final_docs, final_scores):
            if score > 0.2:
                hints.append(doc)

        return "\n".join(hints) if hints else ""
    except Exception:
        logger.exception("에러 패턴 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6) 키워드 의도 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_keyword_intent(question: str, n: int = 3) -> str:
    """키워드→의도 매핑: 후보 6개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("keyword")
    if not coll:
        return ""
    try:
        fetch_n = min(6, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score > 0.2:
                hints.append(
                    f"의도: {meta.get('intent','?')} | 주테이블: {meta.get('table','?')}"
                )

        return "\n".join(hints) if hints else ""
    except Exception:
        logger.exception("키워드 의도 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7) Fewshot 품질관리 저장 (변경 없음)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def save_successful_sql(question: str, sql: str,
                        was_retried: bool = False, retry_count: int = 0):
    """재시도 후 성공한 SQL만 저장. 유사도 0.95 이상 중복 제거.
    200개 초과 시 오래된 것 자동 정리. 저장 후 BM25 인덱스 갱신."""
    coll = rag_colls.get("fewshot")
    if not coll:
        return
    if not was_retried:
        return
    try:
        res = coll.query(query_texts=[question], n_results=1)
        if res["distances"] and res["distances"][0]:
            similarity = 1 - res["distances"][0][0]
            if similarity >= 0.95:
                logger.info(f"Fewshot 중복 스킵 (유사도 {similarity:.3f}): {question[:30]}")
                return

        doc_id = "managed_" + hashlib.md5(question.encode()).hexdigest()[:10]
        meta = {
            "sql": sql,
            "saved_at": datetime.now().isoformat(),
            "retry_count": retry_count,
            "version": 1,
        }
        existing = coll.get(ids=[doc_id])
        if existing["ids"]:
            old_ver = existing["metadatas"][0].get("version", 1)
            meta["version"] = old_ver + 1
            coll.update(ids=[doc_id], documents=[question], metadatas=[meta])
        else:
            coll.add(documents=[question], metadatas=[meta], ids=[doc_id])

        # 200개 초과 시 오래된 것 정리
        if coll.count() > 200:
            all_data = coll.get(include=["metadatas"])
            items = sorted(
                zip(all_data["ids"], all_data["metadatas"]),
                key=lambda x: x[1].get("saved_at", ""),
            )
            to_del = [id_ for id_, _ in items[: coll.count() - 200]]
            if to_del:
                coll.delete(ids=to_del)
                logger.info(f"Fewshot 정리: {len(to_del)}개 삭제")

        # BM25 인덱스 갱신
        _build_bm25_index()

        logger.info(
            f"Fewshot 저장 (재시도 {retry_count}회 후 v{meta['version']}): {question[:30]}"
        )
    except Exception:
        logger.exception("Fewshot 품질관리 저장 실패")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 엔티티 링킹 (오타 보정 + RAG 동의어 통합) — 변경 없음
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def entity_linking_node(state: AgentState):
    q = state["question"]
    refined = q

    # 1차: rapidfuzz 기반 오타 보정
    names = entity_cache["manufacturers"] + entity_cache["vendors"]
    for word in q.split():
        if len(word) >= 2:
            match = process.extractOne(word, names, scorer=fuzz.ratio)
            if match and match[1] > 70:
                refined = refined.replace(word, match[0])

    # 2차: entity_store 벡터 검색으로 part_number 오타 보정
    coll_ent = rag_colls.get("entity")
    if coll_ent:
        try:
            res = coll_ent.query(query_texts=[q], n_results=3)
            for doc, meta, dist in zip(
                res["documents"][0], res["metadatas"][0], res["distances"][0]
            ):
                if dist < 0.15 and meta.get("type") == "part_number":
                    for word in q.split():
                        if len(word) > 5 and word.upper() != doc.upper():
                            match_score = sum(c in doc for c in word) / max(
                                len(word), len(doc)
                            )
                            if match_score > 0.8:
                                refined = refined.replace(word, doc)
                                logger.info(f"part_number 보정: {word} → {doc}")
        except Exception:
            pass

    # 3차: RAG 동의어 사전 힌트 수집
    synonym_hint = rag_retrieve_synonyms(q)
    if synonym_hint:
        logger.info(f"동의어 감지: {synonym_hint}")

    # 구조화 메모리로 대명사/생략 표현 보완
    memory = st.session_state.get("structured_memory", {})
    refined = inject_memory_to_question(refined, memory)

    return {
        "refined_question":  refined,
        "synonym_hint":      synonym_hint,
        "error_history":     [],
        "retry_count":       0,
        "structured_memory": memory,
        "result_anomalies":  [],
        "validation_errors": [],
    }

# ==========================================
# 라우팅 보조: 데이터 관련 키워드 사전 감지
# ==========================================
DATA_KEYWORDS = [
    # 재고/제품
    "재고", "품목", "제품", "상품", "부품", "수량", "현재고", "재고량",
    # 매출/매입
    "매출", "매입", "판매", "구매", "주문", "발주",
    # 분석 동사
    "많은", "적은", "높은", "낮은", "최대", "최소", "평균", "합계", "총",
    "얼마", "몇", "뭐야", "뭐지", "뭔지", "알려줘", "보여줘", "조회",
    "순위", "랭킹", "비교", "분석", "추이", "현황", "통계",
    # 시간
    "이번달", "저번달", "지난달", "올해", "작년", "이번주", "최근",
    "지금", "현재", "오늘",
    # 공급사/판매처
    "공급사", "제조사", "업체", "거래처", "벤더",
]

TECH_SALES_KEYWORDS = [
    "스펙", "사양", "데이터시트", "datasheet", "핀맵", "pinout",
    "대체품", "호환", "equivalent", "alternative",
    "납기", "리드타임", "재고확인", "EOL", "단종",
    "온도범위", "전압", "전류", "패키지", "풋프린트",
    "RoHS", "AEC-Q", "인증", "규격",
    "추천", "제안", "견적",
]

def is_data_question(q: str) -> bool:
    return any(kw in q for kw in DATA_KEYWORDS)

def is_tech_sales(q: str) -> bool:
    return any(kw in q for kw in TECH_SALES_KEYWORDS)

def get_work_context_summary() -> str:
    """최근 업무 대화 맥락 요약 (분류기에 주입용)"""
    work_ctx = st.session_state.get("work_context", [])
    if not work_ctx:
        return ""
    # 최근 4개 메시지만 사용
    recent = work_ctx[-4:]
    lines = []
    for m in recent:
        role = "사용자" if m["role"] == "user" else "AI"
        lines.append(f"{role}: {m['content'][:80]}")
    return "\n".join(lines)

def router_node(state: AgentState):
    q = state["question"]

    # ── 1차: 데이터 키워드 → 즉시 INVENTORY ────────────────────
    if is_data_question(q):
        logger.info(f"라우터: 데이터 키워드 → INVENTORY | {q}")
        return {"intent": "INVENTORY"}

    # ── 2차: 테크니컬 키워드 → 즉시 TECH_SALES ─────────────────
    if is_tech_sales(q):
        logger.info(f"라우터: 기술영업 키워드 → TECH_SALES | {q}")
        return {"intent": "TECH_SALES"}

    # ── 3차: LLM 분류 (업무 맥락 주입으로 후속질문 정확도 향상) ──
    work_ctx = get_work_context_summary()
    ctx_section = f"\n[직전 업무 대화 맥락]\n{work_ctx}" if work_ctx else ""

    prompt = PromptTemplate.from_template("""당신은 전자부품 수입 유통 회사의 AI 챗봇 분류기입니다.
아래 질문을 세 가지 중 하나로만 분류하세요.

INVENTORY  : 재고/매출/매입/수익/품목/고객사/제조사 등 데이터 조회·분석 요청
TECH_SALES : 부품 스펙·사양·대체품·호환성·납기·기술 문의 등 테크니컬 세일즈 요청
CHIT_CHAT  : 업무와 전혀 무관한 일상 대화{ctx_section}

[중요] 직전 업무 대화가 있고 질문이 짧거나 확인성("그래서", "3월은?", "맞아?", "왜?", "다시")이면
→ 직전 업무와 같은 분류로 처리하세요.

[INVENTORY 예시]
- "이번달 매출 얼마야" → INVENTORY
- "재고 현황" → INVENTORY
- "3월은?" (직전: 매출 조회) → INVENTORY
- "맞아?" (직전: 데이터 응답) → INVENTORY

[TECH_SALES 예시]
- "BCM5650의 대체품 있어?" → TECH_SALES
- "이 부품 납기 얼마나 걸려?" → TECH_SALES

[CHIT_CHAT 예시]
- "안녕" → CHIT_CHAT
- "밥 뭐 먹지" → CHIT_CHAT
- "오늘 날씨 어때" → CHIT_CHAT

질문: {q}
분류:""")

    try:
        raw = (prompt | llm | StrOutputParser()).invoke({"q": q, "ctx_section": ctx_section}).strip().upper()
        if "INVENTORY" in raw:
            result = "INVENTORY"
        elif "TECH_SALES" in raw or "TECH" in raw:
            result = "TECH_SALES"
        else:
            result = "CHIT_CHAT"
    except Exception:
        logger.exception("라우터 LLM 실패 → INVENTORY 폴백")
        result = "INVENTORY"

    logger.info(f"라우터: LLM 분류={result} | {q}")
    return {"intent": result}

# 지능형 SQL 생성
def generate_sql_node(state: AgentState):
    prompt = PromptTemplate.from_template("""당신은 PostgreSQL 전문가입니다. 아래 규칙을 반드시 지켜 SQL만 출력하세요.

[필수 규칙]
1. current_products, products 테이블에는 날짜 WHERE 조건을 절대 추가하지 마세요.
2. 날짜 필터는 sales_orders(sale_date), purchase_orders(purchase_date) 에만 사용하세요.
3. 재고 조회(현재 재고, 지금 재고 등)는 current_products를 날짜 필터 없이 조회하세요.
4. SQL 코드만 출력하고 설명, 주석, 마크다운은 절대 포함하지 마세요.
5. 에러가 있었다면 에러 원인을 수정하여 재작성하세요.
6. sales_orders와 purchase_orders 등 독립적인 여러 트랜잭션 테이블에서 동시에 SUM()을 구할떄는 절대 직접 JOIN하지말고, 반드시 WITH절(CTE)을 사용해 각각 따로 집계한후 product 테이블과 JOIN하세요.
7. 부품번호는 반드시 part_number 컬럼에만 = 연산자로 검색하세요
8. 여러 CTE를 합칠 때는 반드시 products 테이블을 FROM에 두고 각 CTE를 LEFT JOIN 하세요. 절대 CTE끼리 FROM절에 쉼표로 나열하지 마세요. (교차 조인 금지)

[연도 처리 규칙] ← 반드시 준수
- "23년", "24년", "25년" 등 두 자리 연도는 모두 2000년대로 해석 (23→2023, 24→2024, 25→2025)
- "N년 동안", "N년에", "N년 한 해" → EXTRACT(YEAR FROM 날짜컬럼) = 20NN
- 연도 필터 예시: WHERE EXTRACT(YEAR FROM sale_date) = 2024
- 절대로 25년을 2050년으로 해석하지 마세요.

[SQL 데이터 타입 규칙]
- 모든 금액 및 수량 합계(SUM)는 반드시 ::BIGINT 또는 ::NUMERIC으로 형변환하여 출력하세요.
- 연도(Year)나 월(Month) 같은 X축 후보 컬럼은 반드시 ::TEXT로 형변환하여 출력하세요. (차트 렌더링 오류 방지)
- 예시: SELECT EXTRACT(YEAR FROM sale_date)::TEXT AS sale_year, SUM(...) AS total_revenue

[분기 처리 규칙]
- 분기 필터: EXTRACT(QUARTER FROM sale_date) = N (N은 1,2,3,4)
- 연도+분기: EXTRACT(YEAR FROM sale_date)=2024 AND EXTRACT(QUARTER FROM sale_date)=1
- DATE_TRUNC과 TO_DATE 중첩 절대 금지 → 단순하게 EXTRACT만 사용

[금액/수치 출력 규칙]
- 모든 금액은 원화(KRW, 원) 기준
- 금액 집계 시 반드시 ROUND(..., 0)::BIGINT 사용 (소수점 제거)
- 날짜 집계 시 DATE_TRUNC 대신 EXTRACT(YEAR FROM ...) 또는 TO_CHAR(..., 'YYYY') 사용
  → DATE_TRUNC 사용 시 타임존 포함 datetime이 출력되어 가독성 저하

[매출 및 수익 산출 절대 규칙] ← 반드시 준수

1. 용어 정의 및 공식 (절대 혼동 금지):
   - 매출(Revenue/Sales): SUM(so.sale_quantity * so.actual_selling_price)
   - 수익(Profit/Net Income): SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost))
   - "데이터가 없어서 계산할 수 없다"는 답변은 절대 금지합니다. DB의 actual_selling_price와 std_unit_cost 컬럼을 사용하여 즉시 계산하세요.

2. JOIN 및 데이터 참조:
   - 수익 계산 시 반드시 sales_orders(so)와 products(p)를 part_number로 JOIN하여 p.std_unit_cost를 가져오세요.
   - '고객사별' 수익/매출 요청 시에는 vendors(v) 테이블을 추가로 JOIN하세요.

3. 시간축 및 집계 처리:
   - 연도별/월별 비교 요청 시, GROUP BY 절에 EXTRACT(YEAR/MONTH FROM so.sale_date)를 반드시 포함하여 데이터가 시계열로 나뉘게 하세요.
   - 단일 연도 합산이 아닌 '추이'나 '비교' 질문 시 CTE(WITH절)를 사용하여 연도별 집계를 분리하세요.

4. 수치 형식 및 단위:
   - 모든 금액 결과는 ROUND(..., 0)::BIGINT를 적용하여 원화(KRW) 정수로 표시하세요.
   - 0원인 경우에도 "데이터 없음" 대신 "0원"으로 명확히 표기하세요.

5. 답변 가이드:
   - 결과 표가 출력되더라도, 답변 텍스트 첫 줄에 핵심 수치(총 매출액 또는 총 수익액)를 반드시 먼저 언급하세요.

[금액 단위 안내 규칙]
- 1,000,000,000 (0이 9개) = 10억 원
- 10,000,000,000 (0이 10개) = 100억 원
- 결과값의 자릿수를 반드시 확인하고 "OO억 원" 단위로 요약하여 답변할 것.
- 데이터 테이블의 수치와 답변 텍스트의 수치가 다를 경우 답변하지 말고 재계산할 것.

[테이블 별칭 고정 규칙] ← 반드시 준수
- sales_orders → 별칭 so (purchase_orders와 혼동 금지)
- purchase_orders → 별칭 po
- products → 별칭 p
- vendors → 별칭 v
- manufacturers → 별칭 m
- current_products → 별칭 cp

[질문 해석 및 사고 방식]
1. 사용자가 "누가 사갔어?", "어떤 고객사가 많이 샀어?"라고 물으면:
   - AI의 판단: "이건 판매(매출)에 대한 질문이다."
   - 액션: 오직 sales_orders와 vendors 테이블만 사용하여 쿼리를 짠다.
   - 절대 금지: 질문에 '구매'라는 단어가 있어도 purchase_orders(매입)를 뒤적거리지 않는다.

2. 사용자가 "어디서 샀어?", "제조사가 어디야?"라고 물으면:
   - AI의 판단: "이건 매입(입고)에 대한 질문이다."
   - 액션: 오직 purchase_orders와 manufacturers 테이블만 사용한다.

3. 답변 구성 방식:
   - "어떤 고객사가 가장 많이 샀습니다. 수량은 OO개입니다."처럼 결론을 먼저 말한다.
   - 만약 데이터가 여러 개라면 상위 순위 위주로 요약해서 답변한다.

[집계 단위 기본값 규칙] ← 반드시 준수
- 사용자가 "제품", "품목", "부품", "part" 언급 시 → GROUP BY part_number (개별 제품 단위)
- 사용자가 "카테고리", "종류", "분류", "description" 언급 시 → GROUP BY description
- 단위 명시가 없을 때 → 기본값은 part_number 단위로 집계
  예) "가장 많이 팔린게 뭐지" → GROUP BY p.part_number (카테고리X, 개별 제품 기준)

[description 필터 규칙] ← 반드시 준수
- description 컬럼은 정확한 코드값만 존재: IC, C_CHIP/CAP, R_CHIP/RES, FET/TR
- 반드시 = 연산자 사용. LIKE, ILIKE 절대 금지
- "IC칩", "아이씨", "집적회로" → WHERE p.description = 'IC'
- "커패시터", "캐패시터", "콘덴서" → WHERE p.description = 'C_CHIP/CAP'
- "저항", "레지스터" → WHERE p.description = 'R_CHIP/RES'

[데이터 타입 규칙]
- 날짜 컬럼은 모두 DATE 타입 → 비교 시 'YYYY-MM-DD' 형식 문자열 사용
- 금액 컬럼(actual_selling_price, actual_unit_cost, std_unit_cost, std_selling_price)은 NUMERIC
- 수량 컬럼(sale_quantity, purchase_quantity, current_quantity, initial_quantity)은 INTEGER
- part_number, vendor_name, name 등 식별자는 VARCHAR

[테이블별 날짜 컬럼 정리]
- sales_orders.sale_date → DATE, 필터 가능
- purchase_orders.purchase_date → DATE, 필터 가능
- initial_inventory.stock_date → DATE, 필터 가능
- current_products.last_updated → DATE, 필터 금지 (항상 전체 조회)

[스키마]{schema}
[매출/매입 데이터 기간] {min_d} ~ {max_d}
[에러기록] {errors}
{ctx_section}{rag}
[질문] {q}

SQL:""")
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

# ==========================================
# 5. UI 렌더링
# ==========================================
with st.sidebar:
    st.header("🏢 AI 관제실")
    st.info(f"📅 데이터 현황: {data_stats.get('min_date')} ~ {data_stats.get('max_date')}")
    fs_coll = rag_colls.get("fewshot")
    if fs_coll:
        fs_cnt  = fs_coll.count()
        syn_cnt = rag_colls["synonym"].count() if rag_colls.get("synonym") else 0
        biz_cnt = rag_colls["bizterm"].count() if rag_colls.get("bizterm") else 0
        bm25_ok = "✅" if _bm25_index is not None else "❌"
        st.success("🧠 RAG 연결됨")
        ent_cnt = rag_colls["entity"].count()  if rag_colls.get("entity")  else 0
        sch_cnt = rag_colls["schema"].count()  if rag_colls.get("schema")  else 0
        err_cnt = rag_colls["error"].count()   if rag_colls.get("error")   else 0
        kw_cnt  = rag_colls["keyword"].count() if rag_colls.get("keyword") else 0
        st.caption(f"Few-shot: {fs_cnt} | 동의어: {syn_cnt} | 용어: {biz_cnt} | 엔티티: {ent_cnt}")
        st.caption(f"스키마: {sch_cnt} | 에러패턴: {err_cnt} | 키워드: {kw_cnt}")
        st.caption(f"하이브리드 검색(BM25): {bm25_ok}")
    else:
        st.warning("⚠️ RAG 비활성화 (rag_builder.ipynb 먼저 실행)")

    # [기능] 빠른 응답을 위한 캐시 현황 표시 및 초기화 버튼
    cache_cnt = len(st.session_state.get("query_cache", {}))
    st.caption(f"⚡ 캐시: {cache_cnt}건 (TTL {CACHE_TTL_MINUTES}분)")
    if st.button("🗑️ 캐시 초기화"):
        cache_invalidate()
        st.success("캐시 초기화 완료")

    # [기능] 대화 문맥 추적용 구조화 메모리 현황 사이드바 표시
    mem = st.session_state.get("structured_memory", {})
    if mem:
        st.caption(f"🧠 메모리: {', '.join(f'{k}={v}' for k,v in list(mem.items())[:3])}")

    # [기능] 세션 ID 발급 (DB 저장용 식별자)
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    st.caption(f"세션 ID: `{st.session_state.session_id[:8]}...`")

# [기능] DB에서 이전 대화 이력 불러와 세션에 복원
if "messages" not in st.session_state:
    persisted = load_session_history(st.session_state.session_id)
    st.session_state.messages = persisted if persisted else [
        {"role": "assistant", "content": "데이터 분석 준비 완료."}
    ]

# [기능] 라우팅 분류기용 순수 업무 대화 이력 보관 리스트 (일상 대화 제외)
if "work_context" not in st.session_state:
    st.session_state.work_context = []

# [기능] 대명사 해석 및 컨텍스트 유지를 위한 구조화 메모리 초기화
if "structured_memory" not in st.session_state:
    st.session_state.structured_memory = {}

# [기능] 중복 질문 DB 부하 방지를 위한 쿼리 캐시 초기화
if "query_cache" not in st.session_state:
    st.session_state.query_cache = {}

# [기능] SQL 결과 설명(Explainability)을 위한 메타데이터 보관
if "last_explain_meta" not in st.session_state:
    st.session_state.last_explain_meta = {}
if "last_question" not in st.session_state:
    st.session_state.last_question = ""


# ==========================================
# [수정] UI 렌더링 헬퍼 함수 (차트 오류 및 단위 환각 방지)
# ==========================================
def render_response(content, sql=None, df=None, info=None):
    st.write(content)
    if sql:
        with st.expander("🔍 실행된 SQL 보기"):
            st.code(sql, language="sql")

    if df is not None and not df.empty:
        # 1. 수치형 데이터 강제 보정
        import pandas as pd
        chart_df = df.copy()

        st.subheader("📋 데이터 테이블")
        st.dataframe(chart_df, use_container_width=True)

        if info and info.get("type") not in (None, "none"):
            x_col = str(info.get("x", "")).strip()
            y_col = str(info.get("y", "")).strip()

            if x_col in chart_df.columns and y_col in chart_df.columns:
                try:
                    # Y축: 강제 숫자화 및 억 단위 변환
                    chart_df[y_col] = pd.to_numeric(chart_df[y_col], errors='coerce').fillna(0)

                    # X축: 범주형(문자열) 확정
                    chart_df[x_col] = chart_df[x_col].astype(str)

                    display_y = y_col
                    if chart_df[y_col].abs().max() >= 100_000_000:
                        display_y = f"{y_col}(억)"
                        chart_df[display_y] = chart_df[y_col] / 100_000_000

                    st.subheader(f"📊 {info['type'].upper()} 리포트")

                    # Streamlit 차트는 인덱스가 아닌 컬럼 지정 방식으로 호출
                    if info["type"] == "bar":
                        st.bar_chart(data=chart_df, x=x_col, y=display_y)
                    elif info["type"] == "line":
                        st.line_chart(data=chart_df, x=x_col, y=display_y)

                except Exception as e:
                    st.error(f"차트 내부 오류: {e}")
# ==========================================
# 기존 메시지 렌더링 및 대화 로직 (동일 유지)
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_response(
                content=msg.get("content", ""),
                sql=msg.get("sql_query"),
                df=msg.get("df"),
                info=msg.get("chart_info")
            )
        else:
            st.write(msg.get("content", ""))

user_input = st.chat_input("질문하세요...")
if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message(st.session_state.session_id, "user", user_input)

    if any(t in user_input for t in EXPLAIN_TRIGGERS) and st.session_state.last_explain_meta:
        explanation = generate_explanation(st.session_state.last_explain_meta, st.session_state.get("last_question", ""))
        st.chat_message("assistant").markdown(explanation)
        st.session_state.messages.append({"role": "assistant", "content": explanation})
        save_message(st.session_state.session_id, "assistant", explanation)
        st.stop()

    cached = cache_get(user_input)
    if cached:
        res = cached
        st.info("⚡ 캐시 응답")
    else:
        with st.spinner("🤖 사고 및 데이터 처리 중..."):
            res = app_agent.invoke({"question": user_input})

            # ==========================================
            # [데이터 클리닝] 수치형 데이터 강제 변환 (차트 오류 및 단위 환각 방지)
            # ==========================================
            if res.get("df") is not None:
                import pandas as pd
                clean_df = res["df"].copy()
                for col in clean_df.columns:
                    # 숫자로 변환 가능한 컬럼은 모두 변환 (에러는 NaN 처리)
                    converted = pd.to_numeric(clean_df[col], errors='coerce')
                    # 컬럼 전체가 문자열이 아닌 경우(숫자가 하나라도 섞인 경우)만 적용
                    if not converted.isna().all():
                        clean_df[col] = converted.fillna(0)
                res["df"] = clean_df # 정제된 데이터를 결과에 반영

            cache_save(user_input, res) # 정제된 데이터가 캐시에 저장됨

    # [기능] 정제된 데이터프레임을 변수에 할당
    df = res.get("df")
    info = res.get("chart_info", {})
    sql_query = res.get("sql_query")
    intent = res.get("intent", "INVENTORY")
    raw_ans = res.get("db_result", "응답 실패")

    if df is not None and len(df) >= QUERY_RESULT_LIMIT:
        st.warning(f"⚠️ 결과가 {QUERY_RESULT_LIMIT:,}건으로 제한되었습니다.")

    ans = "저는 재고·매출·매입 데이터 분석을 도와드립니다." if raw_ans == "__CHIT_CHAT__" else raw_ans

    # [기능] 화면 렌더링 (보정된 데이터 사용)
    with st.chat_message("assistant"):
        render_response(ans, sql=sql_query, df=df, info=info)

    # [기능] 세션 상태 저장 (그래프/표 데이터 포함)
    st.session_state.messages.append({
        "role": "assistant",
        "content": ans,
        "sql_query": sql_query,
        "df": df,
        "chart_info": info
    })
    save_message(st.session_state.session_id, "assistant", ans)

    if intent != "CHIT_CHAT":
        st.session_state.work_context.append({"role": "user", "content": user_input})
        st.session_state.work_context.append({"role": "assistant", "content": ans[:200]})
        st.session_state.work_context = st.session_state.work_context[-20:]

        # 구조화 메모리 업데이트 시에도 정제된 df 사용
        st.session_state.structured_memory = update_structured_memory(
            st.session_state.structured_memory,
            user_input,
            df,
            res.get("query_plan", {}),
            res.get("sql_query", "")
        )
        if res.get("explain_meta"):
            st.session_state.last_explain_meta = res["explain_meta"]
            st.session_state.last_question = user_input