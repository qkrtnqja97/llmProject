# -*- coding: utf-8 -*-
"""
설정 모듈 - 모든 시스템 설정을 중앙에서 관리
LLM 모델 변경 시 이 파일만 수정하면 됨

주요 토큰 및 API 키:
- GOOGLE_API_KEY: Google Gemini API 키 (https://aistudio.google.com)
- LANGSMITH_API_KEY: LangSmith 추적 키 (https://smith.langchain.com)
- HF_TOKEN: Hugging Face 토큰 (모델 다운로드용)
- CHROMA_HOST/PORT/SSL: ChromaDB 원격 서버 설정

⚠️  .env 파일에서 환경변수를 로드합니다 (repository root 또는 현재 디렉토리)
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# .env 파일 로드 (python-dotenv)
try:
    from dotenv import load_dotenv
    
    # .env 파일 탐색: 현재 디렉토리 → 부모 디렉토리 → 모듈 디렉토리
    env_paths = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path(__file__).parent / ".env",
    ]
    
    loaded = False
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path, verbose=False)
            # print 제거 - Streamlit 환경에서 문제 발생
            loaded = True
            break
        
except ImportError:
    # print 제거 - Streamlit 환경에서 문제 발생
    pass

# ==========================================
# API 키 설정 (환경변수에서 로드)
# ==========================================
# ⚠️  필수 토큰들 - .env 파일이나 시스템 환경변수에서 설정 필요
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

# 토큰 검증 (warnings) - print 제거, logger 사용
# if not GOOGLE_API_KEY:
#     logger.warning("GOOGLE_API_KEY가 설정되지 않았습니다. Google LLM을 사용할 수 없습니다.")
# if not LANGSMITH_API_KEY:
#     logger.warning("LANGSMITH_API_KEY가 설정되지 않았습니다. LangSmith 추적이 비활성화됩니다.")
# if not HF_TOKEN:
#     logger.warning("HF_TOKEN이 설정되지 않았습니다. Hugging Face 모델 다운로드가 제한될 수 있습니다.")

# ==========================================
# 데이터베이스 설정
# ==========================================
DATABASE_CONFIG = {
    "USER": os.getenv("DB_USER", "postgres"),
    "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
    "HOST": os.getenv("DB_HOST", "localhost"),
    "PORT": os.getenv("DB_PORT", "5432"),
    "DB_NAME": os.getenv("DB_NAME", "inventory_db"),
    "SCHEMA": os.getenv("DB_SCHEMA", "public"),
}

DATABASE_URL = (
    f"postgresql+psycopg2://{DATABASE_CONFIG['USER']}:{DATABASE_CONFIG['PASSWORD']}"
    f"@{DATABASE_CONFIG['HOST']}:{DATABASE_CONFIG['PORT']}/{DATABASE_CONFIG['DB_NAME']}"
)

# ==========================================
# ChromaDB 벡터 DB 설정
# ==========================================
CHROMA_CONFIG = {
    "PROVIDER": os.getenv("CHROMA_PROVIDER", "http"),  # "persistent", "http", 또는 "ephemeral"
    "PATH": os.getenv("CHROMA_PATH", "/content/local_vdata"),  # 로컬 경로 (persistent 모드 시)
    "HOST": os.getenv("CHROMA_HOST", "keno-acquired-translator-qld.trycloudflare.com"),  # 원격 Chroma 호스트
    "PORT": int(os.getenv("CHROMA_PORT", "443")),  # 원격 Chroma 포트
    "SSL": os.getenv("CHROMA_SSL", "true").lower() == "true",  # SSL 사용 여부
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
    # Azure OpenAI 설정 추가
    "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
    "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "text-embedding-ada-002"),
}

# ChromaDB 컬렉션 이름 (모든 RAG 데이터 저장) - rag_builder.py와 동일
CHROMA_COLLECTIONS = {
    "FEWSHOT": "fewshot_sql",
    "BIZTERM": "bizterm_store",
    "SCHEMA": "table_schema_store",
}

# ==========================================
# LLM 모델 설정 (유지보수 용이)
# ==========================================
@dataclass
class LLMConfig:
    """LLM 모델 설정 - 변경 시 이 클래스만 수정하면 됨"""
    provider: str  # "google", "openai", "ollama", "local" 등
    model_name: str  # 모델명
    temperature: float  # 0 (확정적) ~ 1 (창의적)
    api_key: Optional[str] = None


# 기본 LLM 설정 (Gemini 2.5 Flash)
DEFAULT_LLM_CONFIG = LLMConfig(
    provider="google",
    model_name="gemini-2.5-flash",
    temperature=0.0,
    api_key=GOOGLE_API_KEY,
)

# 로컬 모델 학습용 백업 설정
LOCAL_TRAINING_LLM_CONFIG = LLMConfig(
    provider="ollama",
    model_name="mistral",  # 또는 "llama2", "neural-chat" 등
    temperature=0.3,
)

# ==========================================
# API 설정
# ==========================================
API_CONFIG = {
    "PORT": int(os.getenv("API_PORT", "8501")),
    "HOST": os.getenv("API_HOST", "localhost"),
}

# ==========================================
# RAG 설정
# ==========================================
RAG_CONFIG = {
    "RERANKER_MODEL": os.getenv("RERANKER_MODEL", "rerank-multilingual-v3.0"),  # 코히어 리랭커
    "BM25_USE": True,  # BM25 하이브리드 검색 활성화
    "VECTOR_SEARCH_TOP_K": 10,  # 벡터 검색 후보 개수
    
    # ─── 3단계 계층적 필터링 ───────────────────────────────────
    # Step 1: 병합 점수 (벡터 0.6 + BM25 0.4)로 후보 선정
    "HYBRID_SCORE_THRESHOLD": 0.4,  # 너무 낮은 것만 제외
    "FETCH_MULTIPLIER": 5,  # 후보 선정: fetch_n = n * FETCH_MULTIPLIER
    
    # Step 2: 리랭킹 (Step 1을 통과한 것 전부)
    "RERANK_TOP_N": 20,  # 리랭킹할 최대 개수
    
    # Step 3: 최종 선택 (리랭커 점수 임계값)
    "RERANKER_SCORE_THRESHOLD": 0.5,  # 기존 0.2 → 0.55 → 0.5 (적절한 엄격도)
    
    # ─── 컬렉션별 반환 상위 N개 ───────────────────────────────
    "TOPN_FINAL": 2,  # Few-shot 최종 반환 개수
    "TOPN_BIZTERM": 3,  # 비즈니스 용어 반환 개수
    "TOPN_SCHEMA": 7,  # 스키마 반환 개수
}

# ==========================================
# SQL 설정
# ==========================================
SQL_CONFIG = {
    "MAX_RETRY_COUNT": 2,  # 최대 재시도 횟수
    "QUERY_RESULT_LIMIT": 10_000,  # 쿼리 결과 최대 건수
    "USE_VALIDATORS": True,  # SQL 검증기 활성화
    "STATEMENT_TIMEOUT": 30,  # SQL 실행 타임아웃 (초)
}

# ==========================================
# 캐싱 설정
# ==========================================
CACHE_CONFIG = {
    "TTL_MINUTES": 30,  # 캐시 유효시간 (분)
    "MAX_SIZE": 50,  # 최대 캐시 크기
    "ENABLE": True,  # 캐시 활성화
}

# ==========================================
# 로깅 설정
# ==========================================
LOGGING_CONFIG = {
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "LOG_FILE": os.getenv("LOG_FILE", "app.log"),
    "LOG_FORMAT": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "LOG_MAX_BYTES": 10 * 1024 * 1024,  # 10MB
    "LOG_BACKUP_COUNT": 5,  # 로그 백업 파일 개수
    # 로컬 모델 학습 추적을 위한 별도 로깅
    "TRAINING_LOG_FILE": os.getenv("TRAINING_LOG_FILE", "training.log"),
    "ENABLE_FILE_HANDLER": True,  # 파일 로그 활성화
    "ENABLE_STREAM_HANDLER": True,  # 콘솔 로그 활성화
}

# ==========================================
# 비즈니스 로직 상수
# ==========================================
BUSINESS_LOGIC = {
    "products": """[제품 마스터] 회사가 취급하는 300종 전자부품 핵심 정보.
  - part_number: VARCHAR PK. 부품 고유번호.
  - description: VARCHAR. 부품 카테고리 코드 (IC / FET/TR / C_CHIP/CAP / R_CHIP/RES).
  - std_unit_cost: NUMERIC. 표준 매입 원가.
  - std_selling_price: NUMERIC. 표준 판매가.""",
    "manufacturers": """[제조사/공급처] 부품을 공급하는 제조사 마스터. 총 69개사.
  - manufacturer_id: INTEGER PK.
  - name: VARCHAR UNIQUE. 업체명.""",
    "vendors": """[판매처/고객사] 부품을 구매하는 고객사 마스터. 총 29개사.
  - vendor_id: INTEGER PK.
  - vendor_name: VARCHAR. 고객사명.""",
    "sales_orders": """[판매/매출 이력] 고객사에 부품을 판매한 거래 내역. 총 39,572건.
  - order_id: INTEGER PK.
  - vendor_id: INTEGER FK.
  - part_number: VARCHAR FK.
  - sale_quantity: INTEGER.
  - sale_date: DATE. (범위: 2023-01-04 ~ 2025-12-31)
  - actual_selling_price: NUMERIC.""",
    "purchase_orders": """[구매/매입 이력] 제조사로부터 부품을 매입한 거래 내역. 총 13,615건.
  - purchase_id: INTEGER PK.
  - manufacturer_id: INTEGER FK.
  - part_number: VARCHAR FK.
  - purchase_quantity: INTEGER.
  - purchase_date: DATE.
  - actual_unit_cost: NUMERIC.""",
}

# 테이블별 JOIN 규칙 (Cartesian Product 방지)
VALID_JOINS = {
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
    frozenset(['purchase_orders', 'manufacturers']): 'manufacturer_id',
    frozenset(['sales_orders', 'vendors']): 'vendor_id',
}

# ==========================================
# 키워드 분류 설정
# ==========================================
DATA_KEYWORDS = [
    "재고", "품목", "제품", "상품", "부품", "수량", "현재고", "재고량",
    "매출", "매입", "판매", "구매", "주문", "발주",
    "많은", "적은", "높은", "낮은", "최대", "최소", "평균", "합계", "총",
    "얼마", "몇", "뭐야", "뭐지", "뭔지", "알려줘", "보여줘", "조회",
    "순위", "랭킹", "비교", "분석", "추이", "현황", "통계",
    "이번달", "저번달", "지난달", "올해", "작년", "이번주", "최근",
    "지금", "현재", "오늘",
    "공급사", "제조사", "업체", "거래처", "벤더",
]

TECH_SALES_KEYWORDS = [
    "스펙", "사양", "데이터시트", "datasheet", "핀맵", "pinout",
    "대체품", "호환", "equivalent", "alternative",
    "납기", "리드타임", "재고확인", "EOL", "단종",
    "온도범위", "전압", "전류", "패키지", "풋프린트",
    "RoHS", "AEC-Q", "인증", "규격", "추천", "제안", "견적",
]

EXPLAIN_TRIGGERS = ["어떻게 계산", "왜 이 값", "어떻게 나온", "설명해줘", "근거", "어떻게 구한"]

CHART_KEYWORDS = [
    "그래프", "차트", "그려", "시각화", "plot", "chart", "graph",
    "막대", "선그래프", "파이", "도표", "그림", "보여줘", "표시"
]

# ==========================================
# 시스템 상수
# ==========================================
SYSTEM_CONSTANTS = {
    "MAX_WORKERS": 6,  # 병렬 처리 스레드 수 (RAG)
    "THREAD_POOL_TIMEOUT": 3.0,  # 스레드 타임아웃 (초)
}
