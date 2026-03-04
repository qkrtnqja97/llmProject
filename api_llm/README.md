#  api_llm - 엔터프라이즈 AI 에이전트 시스템 (v2.0)

##  프로젝트 개요

전자부품 유통사의 재고매출매입 데이터를 자연어로 분석하는 **엔터프라이즈급 AI 에이전트** 시스템입니다.  
사용자가 한국어로 질문하면, LangGraph 워크플로우가 자동으로 SQL을 생성해 PostgreSQL에서 데이터를 조회하고, Plotly 차트로 시각화하여 답변합니다.

기존 `api.py`(2346줄) 단일 파일을 **모듈화구조화**하여 유지보수와 확장이 용이한 엔터프라이즈 시스템으로 재편했습니다.

### 핵심 특징

| 특징 | 설명 |
|------|------|
| **자연어  SQL** | Google Gemini 2.5 Flash가 한국어 질문을 PostgreSQL 쿼리로 변환 |
| **3단계 RAG** | Few-shot 예제  비즈니스 용어  테이블 스키마를 ChromaDB에서 검색 후 SQL 생성에 주입 |
| **하이브리드 검색** | 벡터(60%) + BM25(40%) 혼합 후 Cohere 리랭킹 |
| **7단계 SQL 검증** | sqlglot 파싱  GROUP BY  Cartesian Product  컬럼 소속 등 자동 검증 |
| **자동 차트 생성** | LLM이 질문과 데이터를 보고 BAR / LINE / PIE / TABLE 자동 선택 (이중 Y축 지원) |
| **대화 메모리** | PostgreSQL + 세션 메모리로 이전 대화 맥락 유지 (Hot 1개월 / Cold 6개월+) |
| **학습 데이터 수집** | 모든 쿼리를 JSONL + DB에 자동 저장, / 피드백으로 로컬 모델 파인튜닝 준비 |
| **멀티 LLM** | Google Gemini / Ollama (로컬) / OpenAI  단일 설정 파일로 전환 |
| **Cloudflare Tunnel** | 원격 PostgreSQL + ChromaDB에 cloudflared 클라이언트 자동 시작으로 안전 터널링 |
| **다중 질문 분리** | 복합 질문을 독립성 판단 후 자동 분리하여 각각 처리 |

---

##  전체 폴더 구조

```
llmProject/
 requirements.txt                    # Python 패키지 목록

 api_llm/                            #  메인 애플리케이션 패키지
    __init__.py
    app.py                          # Streamlit 메인 앱 (849줄)
    config.py                       #  모든 설정 중앙 관리 (278줄)
    db_init.py                      # 앱 시작 시 PostgreSQL + ChromaDB 자동 연결
   
    models/                         # LLM & 벡터 DB 관리
       llm_config.py               # LLM 팩토리 (Google/Ollama/OpenAI) + LangSmith 추적
       vector_db.py                # ChromaDB 싱글톤 관리 + Azure OpenAI 임베딩
   
    sql/                            # SQL 파이프라인
       sql_validator.py            # 7단계 SQL 검증 (sqlglot AST 기반)
       sql_generator.py            # LLM 기반 SQL 생성 + tenacity 재시도
       sql_executor.py             # DB 연결실행캐싱 + Cloudflare Tunnel 자동 시작
   
    rag/                            # 검색 증강 생성 (RAG)
       retrievers.py               # 3컬렉션 하이브리드 검색 + Cohere 리랭킹
   
    agent/                          # LangGraph 에이전트
       state.py                    # AgentState TypedDict 정의 (25개 필드)
       nodes.py                    # 7개 처리 노드 + 다중 질문 분리 (1018줄)
   
    cache/                          # 쿼리 캐싱
       query_cache.py              # TTL 기반 QueryCache + RAGCache
   
    memory/                         # 대화 메모리
       conversation_memory.py      # PostgreSQL 영속화 + 세션 캐시 + 유사 질문 감지
   
    log_config/                     # 로깅 설정
       logger_config.py            # 메인 로그 + 학습 로그 설정
   
    utils/                          # 공통 유틸리티
        helpers.py                  # 차트 추론  결과 설명  구조화 메모리  엔티티 링킹
        training_logger.py          #  학습 데이터 JSONL + DB 이중 저장

 rag_project/                        #  RAG 데이터 빌더
    config.py                       # RAG 빌더 전용 설정
    rag_builder.py                  # ChromaDB 컬렉션 빌드 CLI
    data/
        fewshot_examples.py         # 질문-SQL 예제 (few-shot)
        bizterms.py                 # 비즈니스 용어 사전
        table_schemas.py            # 테이블 스키마 문서
        entity_embeddings.py        # 제조사/고객사 엔티티 목록

 logs/
     training_data.jsonl             # 학습 데이터 누적 로그 (JSONL)
```

---

##  데이터베이스 구조

### PostgreSQL 스키마

#### `inventory_mgmt` 스키마  비즈니스 데이터

| 테이블 | 행 수 | 설명 |
|--------|-------|------|
| `products` | 300건 | 전자부품 마스터 (part_number, description, 표준원가/판매가) |
| `manufacturers` | 69개사 | 부품 공급처 (제조사). PK: manufacturer_id |
| `vendors` | 29개사 | 부품 구매처 (고객사). PK: vendor_id |
| `sales_orders` | 39,572건 | 매출 이력 (2023-01-04 ~ 2025-12-31). 매출 = actual_selling_price  sale_quantity |
| `purchase_orders` | 13,615건 | 매입 이력. 매입 = actual_unit_cost  purchase_quantity |
| `current_products` | - | 현재 재고 스냅샷 |
| `initial_inventory` | - | 초기 재고 |

#### `sql_assistant` 스키마  시스템 데이터

| 테이블 | 설명 |
|--------|------|
| `conversations` | 대화 히스토리 (Hot: 1개월 보관, 맥락 파악용) |
| `request_logs` | 모든 쿼리 로그 (영구 보관, 로컬 모델 학습용) |

#### 테이블 간 JOIN 관계

```
products  part_number  sales_orders
          part_number  purchase_orders
          part_number  current_products
          part_number  initial_inventory

sales_orders     vendor_id         vendors
purchase_orders  manufacturer_id   manufacturers
```

### ChromaDB 컬렉션

| 컬렉션 이름 | 내용 | 검색 전략 |
|------------|------|----------|
| `fewshot_sql` | 질문-SQL 예제 쌍 | Top-N (상위 2개) |
| `bizterm_store` | 비즈니스 용어 사전 | 리랭킹 점수  0.5 (상위 3개) |
| `table_schema_store` | 테이블컬럼 설명 | 리랭킹 점수  0.5 (상위 7개) |
| `entities` | 제조사/고객사 명칭 + 임베딩 | 엔티티 링킹 전용 |

---

##  LangGraph 워크플로우 상세

### 에이전트 실행 흐름

```
사용자 입력
    
    
[다중 질문 분리]
  LLM 독립성 판단 또는 휴리스틱 (연도 차이, 엔티티 차이, 독립 키워드 감지)
    
      (각 질문별 독립 실행)

[1] entity_linking_node   질문 정제
    - rapidfuzz 기반 오타 보정 (제조사/고객사 명칭 매칭)
    - sentence-transformers 벡터 기반 유사 엔티티 검색
    - 구조화 메모리 주입 (이전 필터 조건 재활용)
    - 대명사("그거", "이전 것")  실제 대상 치환
    - 간단한 질문(15자 이하 숫자/날짜)  스킵 (속도 최적화)
    
    
[2] router_node   의도 분류
    - 1차: 키워드 매칭 (DATA_KEYWORDS 37개, TECH_SALES_KEYWORDS 21개)
    - 2차: LLM 분류 (INVENTORY / TECH_SALES / CHIT_CHAT)
    - 최근 대화 맥락 포함하여 분류 정확도 향상
    
     CHIT_CHAT / TECH_SALES  [7] answer_node
    
     INVENTORY
         
         
[3] sql_generation_node   SQL 생성
    ThreadPoolExecutor 병렬 실행 (max_workers=3):
    
     스레드 1: 대화 맥락 로딩 (DB 최근 5개)  
     스레드 2: 스키마 RAG 검색               
     스레드 3: Few-shot + 용어 RAG 검색      
    
     Gemini 2.5 Flash로 CTE 구조 SQL 생성
     tenacity 지수 백오프 재시도 (최대 2회, 2~10초)
     오류 히스토리 기반 전략적 재시도 (syntax / logic)
    
    
[4] db_execution_node   SQL 검증 + 실행
    7단계 정적 검증:
      [1] sqlglot PostgreSQL 다이얼렉트 파싱
      [2] SELECT * 감지  컬럼 명시 요청
      [3] GROUP BY 누락 감지 (CTE 내부 허용)
      [4] Cartesian Product 감지 (JOIN수 vs ON수)
      [5] 컬럼 소속 검증 (AST, regex 폴백)
      [6] JOIN 키 매핑 검증 (VALID_JOINS dict)
      [7] 자동 LIMIT 추가 (상한 10,000건)
     SQLAlchemy 커넥션 풀로 PostgreSQL 실행 (timeout 30초)
     학습 로그 자동 기록 (JSONL + sql_assistant.request_logs)
    
     에러  [3] 재시도 (MAX_RETRY_COUNT=2 한도)
    
     성공
         
         
[5] result_validation_node   결과 검증
    - 빈 DataFrame 감지
    - 비정상 수치 감지 (음수 재고량 등)
     이상 감지 시 [3] 재시도
    
    
[6] visualization_node   시각화 결정
    LLM이 질문 + DataFrame 컬럼/샘플을 분석하여:
    - chart type: bar / line / pie / table / none
    - xKey: X축 컬럼명
    - dataKeys: Y축 컬럼명 목록
    - useSecondaryAxis: 이중 Y축 여부
    - yAxes: 컬럼별 primary/secondary 배정
    - title: 차트 제목
    
    
[7] answer_node   최종 답변 생성
    - LLM으로 데이터 기반 서술형 한국어 답변
    - CHIT_CHAT: 자연스러운 일상 대화
    - TECH_SALES: 기술/영업 전문 답변

    
    
[Streamlit 렌더링]
    - 텍스트 답변
    -  SQL 접기/펼치기
    -  데이터 테이블 (st.dataframe)
    -  Plotly 차트 (BAR/LINE/PIE/이중 Y축)
    -  좋아요 /  싫어요 피드백 버튼
    
    
[피드백 처리]
      user_satisfaction = +1 저장
      user_satisfaction = -1 저장
```

---

##  RAG 시스템 상세

### 3단계 계층적 필터링 파이프라인

```
질문 입력
    
    
[Step 1] 하이브리드 후보 선정
     벡터 검색: ChromaDB 코사인 유사도 (가중치 60%)
     BM25 검색: rank-bm25 Okapi (가중치 40%)
          두 점수 병합 (fetch_n = topN  FETCH_MULTIPLIER)
          HYBRID_SCORE_THRESHOLD=0.4 미만 제거
    
    
[Step 2] Cohere 리랭킹
    cohere.ClientV2.rerank(model="rerank-multilingual-v3.0")
    RERANK_TOP_N=20 문서에 대해 쿼리-문서 교차 인코딩
    
    
[Step 3] 최종 선택
    RERANKER_SCORE_THRESHOLD=0.5 미만 제거
    컬렉션별 상위 N개만 반환:
      FEWSHOT: 2개 / BIZTERM: 3개 / SCHEMA: 7개
```

### BM25 인덱스 초기화 (모듈 로드 시 1회)

```python
# 모든 컬렉션 문서를 공백 토큰화하여 BM25Okapi 인덱스 구축
# ChromaDB에서 전체 문서 로드  메모리 내 인덱스 유지
_bm25_indices["FEWSHOT"]["index"] = BM25Okapi(tokenized_docs)
```

### SQL 프롬프트 내 RAG 주입 예시

```
[RAG]
=== Few-Shot Examples ===
Q: 고객사별 매출 상위 5개는?
SQL: WITH ranked AS (
       SELECT v.vendor_name,
              SUM(s.actual_selling_price * s.sale_quantity) AS revenue,
              RANK() OVER (ORDER BY SUM(...) DESC) AS rnk
       FROM inventory_mgmt.sales_orders s
       JOIN inventory_mgmt.vendors v USING(vendor_id)
       GROUP BY v.vendor_name
     )
     SELECT vendor_name, revenue FROM ranked WHERE rnk <= 5;

=== Business Terms ===
- 매출: actual_selling_price  sale_quantity (sales_orders 테이블)
- 매입: actual_unit_cost  purchase_quantity (purchase_orders 테이블)

=== Relevant Schemas ===
sales_orders: order_id, vendor_id, part_number, sale_quantity, sale_date, actual_selling_price
vendors: vendor_id, vendor_name
products: part_number, description, std_unit_cost, std_selling_price
```

---

##  SQL 검증 7단계 상세

```python
# [1] sqlglot 구문 파싱 (진짜 SQL 문법 오류 감지)
try:
    sqlglot.parse_one(sql, dialect="postgres")
except ParseError as e:
    return False, f"SQL 문법 오류: {str(e)[:200]}"

# [2] SELECT * 감지
if re.search(r'SELECT\s+\*', sql_upper):
    errors.append("SELECT * 금지  필요한 컬럼을 명시하세요")

# [3] GROUP BY 누락 감지 (CTE 내 집계 허용, 마지막 SELECT 기준 검사)
if has_agg and not has_grp and not has_win:
    has_agg_in_final_select = ...
    if non_agg_cols and has_agg_in_final_select:
        errors.append("GROUP BY 누락: 비집계 컬럼 존재")

# [4] Cartesian Product 감지 (CROSS JOIN 제외 카운트)
cross_join_cnt = len(re.findall(r'\bCROSS\s+JOIN\b', sql_upper))
join_cnt = len(re.findall(r'\bJOIN\b', sql_upper)) - cross_join_cnt
on_cnt = len(re.findall(r'\bON\b|\bUSING\b', sql_upper))
if join_cnt > on_cnt:
    errors.append(f"Cartesian Product 위험: JOIN {join_cnt}개, ON {on_cnt}개")

# [5] 컬럼 소속 검증 (sqlglot AST 우선, 실패 시 regex 폴백)
for col in tree.find_all(sqlglot.exp.Column):
    if col.name not in valid_cols_for_table:
        hint = f"'{col.name}'이 '{actual_table}'에 없음"
        if found_in_other_table:
            hint += f"  '{other_table}'에 존재. JOIN 필요"
        errors.append(hint)

# [6] JOIN 키 매핑 (config.py의 VALID_JOINS dict 참조)
VALID_JOINS = {
    frozenset(['sales_orders', 'vendors']): 'vendor_id',
    frozenset(['purchase_orders', 'manufacturers']): 'manufacturer_id',
    frozenset(['products', 'sales_orders']): 'part_number',
    ...
}

# [7] 자동 LIMIT
if "LIMIT" not in sql_upper:
    sql += f"\nLIMIT {SQL_CONFIG['QUERY_RESULT_LIMIT']}"  # 기본 10,000
```

---

##  자동 시각화 시스템

### 차트 타입 결정 우선순위

| 우선순위 | 조건 | 차트 | 예시 |
|----------|------|------|------|
| 1 | 질문에 "파이/비율/점유/pie" | PIE | "고객사별 매출 비중" |
| 2 | 질문에 "추이/변화/흐름/트렌드/선/월별/일별/시계열" | LINE | "월별 매출 추이" |
| 3 | 질문에 "판매/수량/매출/비교/순위/top" | BAR | "판매 상위 10개 부품" |
| 4 | DataFrame에 datetime 컬럼 존재 | LINE | 날짜 포함 결과 |
| 5 | 기본값 | BAR | 그 외 모든 경우 |

### 이중 Y축 차트 (Dual Axis)

```python
# visualization_node가 생성하는 chart_info 예시
{
    "type": "bar",
    "title": "분기별 매출금액 및 판매수량",
    "xKey": "quarter",
    "dataKeys": ["revenue", "quantity"],
    "useSecondaryAxis": True,
    "yAxes": {
        "revenue": "primary",    # 좌측 Y축 (파란색)
        "quantity": "secondary"  # 우측 Y축 (빨간색)
    },
    "data": [
        {"quarter": "2023Q1", "revenue": 1200000, "quantity": 450},
        ...
    ]
}
```

### X축 자동 포맷팅 (`_format_xaxis_data`)

```python
# datetime 컬럼  "2023년 Q1" 형식
df["xKey"] = df["year"].astype(str) + "년 " + "Q" + df["xKey"].dt.quarter.astype(str)

# 별도 year + quarter 컬럼  자동 결합
if "year" in df.columns and "quarter" in df.columns:
    df["xKey"] = df["year"].astype(str) + "년 " + df["quarter"].astype(str)
```

---

##  대화 메모리 시스템

### 2계층 저장 구조

```
세션 메모리 (in-memory, ConversationMemory)
    - 현재 세션 대화 최대 100개
    - 질문 임베딩 캐싱 (reuse across similarity checks)
    - 유사 질문 검색: cosine similarity  0.85  캐시 응답 반환
    
     (모든 대화 실시간 동기화)
PostgreSQL (sql_assistant 스키마)
     conversations (Hot, 1개월)
         - question, response_summary, sql_query
         - session_id, user_id, created_at
         - intent, refined_question, row_count, execution_success
    
     request_logs (Cold, 영구)
          - question, generated_sql, schema_snapshot
          - execution_success, execution_result_summary
          - user_satisfaction (-1/0/1/null)
          - error_details, metadata, created_at
```

### 유사 질문 감지 & 캐시 히트

```python
# similarity_threshold=0.85 (엄격한 기준)
cached = memory.find_similar_question("23년 총 매출액이 얼마야?")
# 기존 질문 "2023년 매출은?"  cosine similarity 0.91  캐시 히트
#  저장된 SQL 실행 없이 즉시 응답 + " 이전 결과를 사용합니다" 표시
```

### DB 수명주기 관리

```python
# 1개월 초과 conversations  archive 이동
memory.archive_expired_conversations()
#  {"archived": 15, "message": "15개 대화 아카이빙 완료"}

# 학습 데이터 JSON 내보내기 (Streamlit 다운로드 버튼 연동)
memory.export_training_data("training_export.json")
```

---

##  학습 데이터 수집 시스템

### 이중 자동 저장

| 저장소 | 위치 | 특징 |
|--------|------|------|
| **파일 (백업)** | `logs/training_data.jsonl` | 오프라인 활용, DB 장애 시 복구 |
| **DB (운영)** | `sql_assistant.request_logs` | 온라인 조회, 실시간 통계 |

### JSONL 레코드 구조

```json
{
  "timestamp": "2025-02-27T10:30:45.123456",
  "question": "2023년 분기별 매출액은?",
  "generated_sql": "WITH q AS (\n  SELECT DATE_TRUNC('quarter', sale_date) AS q_date, ...",
  "schema_snapshot": "inventory_mgmt.sales_orders: order_id, vendor_id, part_number, ...",
  "execution_success": true,
  "execution_result_summary": "4행 반환",
  "user_satisfaction": 1,
  "error_details": null,
  "metadata": {
    "retry_count": 0,
    "cache_hit": false,
    "intent": "INVENTORY"
  }
}
```

### 피드백  학습 데이터 흐름

```
[SQL 실행 완료]
     user_satisfaction = null 로 자동 저장
    
    
[Streamlit UI에  /  버튼 표시]
    
      클릭  user_satisfaction = +1
                    positive 학습 샘플
    
      클릭  user_satisfaction = -1
                     negative 샘플 (개선 필요, 재학습 표적)

[로컬 모델 파인튜닝]
    from api_llm.utils.training_logger import log_training_data
    #  SQL 실패 패턴 학습
    #  사용자 선호 SQL 스타일 반영
```

### 최근 대화 조회 (맥락 제공용)

```python
from api_llm.utils.training_logger import get_recent_conversations

recent = get_recent_conversations(limit=5)
#  sql_assistant.conversations 테이블에서
#    최근 1개월 내 5개 대화 조회 (최신순)
#  agent의 context 필드에 주입  SQL 생성 시 맥락 반영
```

---

##  LLM 멀티 프로바이더

### 지원 프로바이더

| 프로바이더 | 클래스 | 기본 모델 | 용도 |
|----------|--------|---------|------|
| `google` | `GoogleLLMProvider` | `gemini-2.5-flash` | 운영 환경 (빠르고 저렴) |
| `ollama` | `OllamaLLMProvider` | `mistral` | 로컬 학습 (API 불필요) |
| `openai` | `OpenAILLMProvider` | `gpt-4o` | 대체 운영 환경 |

### Provider 싱글톤 팩토리

```python
# models/llm_config.py
class LLMFactory:
    _instances = {}  # (provider, model_name)  LLM 인스턴스 캐시

    @classmethod
    def get_llm(cls, config: LLMConfig):
        cache_key = (config.provider, config.model_name)
        if cache_key not in cls._instances:
            cls._instances[cache_key] = LLM_PROVIDERS[config.provider].get_model(config)
        return cls._instances[cache_key]

    @classmethod
    def switch_model(cls, config):
        # 기존 캐시 제거  새 모델 초기화
        del cls._instances[(config.provider, config.model_name)]
        return cls.get_llm(config)
```

### LangSmith 추적 (자동 설정)

```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "api_llm_enterprise_ai"
#  모든 LLM 호출이 LangSmith 대시보드에 자동 기록
#  토큰 사용량, 레이턴시, 오류 추적 가능
```

---

##  ChromaDB & 임베딩

### 연결 모드

| 모드 | 설정값 | 설명 |
|------|--------|------|
| **HTTP** (기본) | `CHROMA_PROVIDER=http` | Cloudflare Tunnel 경유 원격 서버 접속 |
| **Persistent** | `CHROMA_PROVIDER=persistent` | 로컬 파일 시스템 저장 |
| **Ephemeral** | `CHROMA_PROVIDER=ephemeral` | 메모리 전용 (테스트) |

### 임베딩 함수 자동 선택

```python
# Azure OpenAI 키가 있으면  text-embedding-ada-002 (Azure 배포)
# 없으면  SentenceTransformer 로컬 모델
if azure_key and ("ada" in model_name or "openai" in model_name.lower()):
    ef = OpenAIEmbeddingFunction(api_type="azure", ...)
else:
    ef = SentenceTransformerEmbeddingFunction(model_name=model_name)
```

### 엔티티 링킹용 임베딩 캐시

```python
# 앱 시작 시 ChromaDB entities 컬렉션에서 임베딩 벡터 로드
# distiluse-base-multilingual-cased-v2 모델로 실시간 벡터 비교
embeddings_data = {
    "model": SentenceTransformer("distiluse-base-multilingual-cased-v2"),
    "entities": ["삼성전자", "LG", "SK하이닉스", ...],  # 69+29개 엔티티
    "embeddings": np.array([...], dtype=np.float32),   # 사전 계산된 벡터
}
#  entity_linking_node에서 입력 텍스트와 코사인 유사도 비교  오타 보정
```

---

##  Cloudflare Tunnel 자동 연결

```python
# sql/sql_executor.py - DatabaseManager 초기화 시 자동 실행

# .env의 CLOUDFLARE_DB_HOST가 trycloudflare.com 도메인이면:
# 1. psutil로 기존 cloudflared 프로세스 실행 여부 확인
# 2. 없으면 백그라운드에서 자동 시작:
cmd = [
    "cloudflared", "access", "tcp",
    "--hostname", cloudflare_host,   # 원격 Cloudflare URL
    "--url", "tcp://127.0.0.1:5432"  # 로컬 포트 포워딩
]
# Windows: CREATE_NO_WINDOW 플래그 (숨김 실행)
# Linux: os.setsid() (세션 분리)
#  3초 대기 후 DB 연결 시도
```

---

##  주요 설정값 (`config.py`)

### LLM 설정

```python
DEFAULT_LLM_CONFIG = LLMConfig(
    provider="google",            # "google" / "ollama" / "openai"
    model_name="gemini-2.5-flash",
    temperature=0.0,              # 0.0: 결정적(SQL 생성에 적합)
    api_key=GOOGLE_API_KEY,
)
LOCAL_TRAINING_LLM_CONFIG = LLMConfig(
    provider="ollama",
    model_name="mistral",         # 로컬 모델 (API 없이 실행)
    temperature=0.3,
)
```

### RAG 설정 (3단계 임계값)

```python
RAG_CONFIG = {
    "RERANKER_MODEL": "rerank-multilingual-v3.0",  # Cohere 리랭커
    "HYBRID_SCORE_THRESHOLD": 0.4,  # Step1: 하이브리드 후보 선정
    "FETCH_MULTIPLIER": 5,          # Step1: fetch_n = topN  5
    "RERANK_TOP_N": 20,             # Step2: 리랭킹 대상 수
    "RERANKER_SCORE_THRESHOLD": 0.5,# Step3: 최종 컷오프
    "TOPN_FINAL": 2,                # Few-shot 최종 반환
    "TOPN_BIZTERM": 3,              # 용어 최종 반환
    "TOPN_SCHEMA": 7,               # 스키마 최종 반환
}
```

### SQL 설정

```python
SQL_CONFIG = {
    "MAX_RETRY_COUNT": 2,         # 최대 재시도 횟수
    "QUERY_RESULT_LIMIT": 10_000, # 자동 LIMIT 상한
    "USE_VALIDATORS": True,       # 7단계 검증 활성화
    "STATEMENT_TIMEOUT": 30,      # DB 실행 타임아웃 (초)
}
```

### 비즈니스 로직 상수

```python
VALID_JOINS = {
    frozenset(['products', 'sales_orders']): 'part_number',
    frozenset(['products', 'purchase_orders']): 'part_number',
    frozenset(['sales_orders', 'vendors']): 'vendor_id',
    frozenset(['purchase_orders', 'manufacturers']): 'manufacturer_id',
    ...  # 12개 테이블 쌍 조합
}

DATA_KEYWORDS = [
    "재고", "매출", "매입", "판매", "수량", "얼마", "순위", ...  # 37개
]
TECH_SALES_KEYWORDS = [
    "스펙", "데이터시트", "대체품", "납기", "RoHS", ...  # 21개
]
```

---

##  설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

```dotenv
# .env 파일 (프로젝트 루트)

#  필수 
GOOGLE_API_KEY=your_google_gemini_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
COHERE_API_KEY=your_cohere_api_key

#  PostgreSQL 
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inventory_db
DB_SCHEMA=inventory_mgmt

#  ChromaDB 
CHROMA_PROVIDER=http
CHROMA_HOST=your-chroma.trycloudflare.com
CHROMA_PORT=443
CHROMA_SSL=true

#  Azure OpenAI 임베딩 (선택사항) 
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_DEPLOYMENT_NAME=text-embedding-ada-002
EMBEDDING_MODEL=text-embedding-ada-002

#  Cloudflare Tunnel (원격 DB) 
CLOUDFLARE_DB_HOST=your-db.trycloudflare.com

#  기타 
LOG_LEVEL=INFO
HF_TOKEN=your_hf_token
```

### 3. ChromaDB 컬렉션 빌드 (최초 1회)

```bash
cd rag_project

# 전체 빌드 (fewshot, bizterm, table_schema, entities)
python rag_builder.py

# 특정 컬렉션만 재빌드
python rag_builder.py --collections fewshot bizterm

# 기존 데이터 삭제 후 전체 재빌드
python rag_builder.py --reset
```

### 4. 앱 실행

```bash
# 프로젝트 루트에서 (sys.path 자동 설정)
streamlit run api_llm/app.py

# 외부 접속 허용 + 포트 지정
streamlit run api_llm/app.py --server.address 0.0.0.0 --server.port 8501
```

---

##  Streamlit UI 구성

### 사이드바

| 섹션 | 내용 |
|------|------|
| ** 시스템 상태** | PostgreSQL 연결 상태 (/), DB명호스트스키마 |
| ** 연결 정보** | 상세 연결 정보 (expander) |
| **RAG 상태** | 3개 컬렉션 문서 수 |
| ** 대화 메모리 & DB** | 세션 대화 수 / Hot 1개월 / 학습 데이터 건수 |
| ** 대화 히스토리** | 최근 5개 대화 조회 (checkbox  expander) |
| ** DB 관리** | 아카이빙 실행 버튼, 학습 데이터 내보내기 + 다운로드 |
| **세션 초기화** | 메모리 전체 삭제 (`st.rerun()` 실행) |

### 채팅 기능

- 이전 대화 히스토리 (SQL테이블차트 포함) 유지 표시
- 유사 질문 감지   캐시 응답 즉시 반환
- 복합 질문 `n`개 자동 분리  `n`개 독립 답변
- ` 실행된 SQL 보기` (expander)
- ` 데이터 테이블` (st.dataframe, 전체 너비)
- Plotly 차트 (단일이중 Y축, BAR/LINE/PIE)
-  /  만족도 버튼 (SQL 결과가 있는 경우만 표시)

---

##  사용 예시

### 질문 유형별 처리

| 질문 | 의도 | 처리 결과 |
|------|------|----------|
| "2023년 분기별 매출은?" | INVENTORY | LINE 차트 + 테이블 |
| "고객사별 매출 비중 상위 5개" | INVENTORY | PIE 차트 + 테이블 |
| "삼성전기 납품 부품 스펙은?" | TECH_SALES | 텍스트 답변 |
| "안녕하세요" | CHIT_CHAT | 텍스트 답변 |
| "2024년 매출은? 2025년 매입은?" | INVENTORY2 | 2개 분리 처리 |

### SQL 생성 프롬프트 핵심 규칙

```
1. 반드시 스키마 명세 기반으로만 쿼리 작성 (추측 금지)
2. 대량 조인 금지  CTE에서 사전 집계 후 JOIN
3. 집계 결과에 COALESCE(..., 0) 적용
4. CTE 3단계 구조: 조회  집계  최종 계산
5. 날짜 월별 집계: DATE_TRUNC('month', ...) 사용 (EXTRACT+MAKE_DATE 금지)
6. 모든 테이블에 스키마 접두사: inventory_mgmt.*
7. 결과에 part_number + description 함께 포함
```

---

##  RAG 빌더 (`rag_project/`)

### 컬렉션 빌드 레지스트리

```python
BUILD_REGISTRY = {
    "fewshot":      (FEWSHOT_EXAMPLES,  prepare_fewshot),
    "bizterm":      (BIZTERM_DATA,      prepare_bizterm),
    "table_schema": (TABLE_SCHEMA_DATA, prepare_table_schema),
    "entities":     (ENTITY_DATA,       prepare_entities),
}
```

### 데이터 형식

```python
# data/fewshot_examples.py
FEWSHOT_EXAMPLES = [
    {"q": "고객사별 매출 순위 상위 5개", "sql": "WITH ranked AS ..."},
]
# ChromaDB 저장: docs=[질문텍스트], metas=[{"sql": ..., "source": "fewshot"}]

# data/bizterms.py
BIZTERM_DATA = [
    {"term": "매출", "desc": "actual_selling_price  sale_quantity"},
    {"term": "수익률", "desc": "(판매가 - 매입원가) / 판매가  100"},
]
# ChromaDB 저장: docs=["매출: actual_selling_price  ..."], metas=[{"term":..., "desc":...}]

# data/table_schemas.py
TABLE_SCHEMA_DATA = [
    {
        "id": "sales_orders",
        "description": "고객사에 부품을 판매한 거래 내역 (39,572건)",
        "columns": "order_id INT PK, vendor_id INT FK, part_number VARCHAR FK, ...",
        "sql": "SELECT * FROM inventory_mgmt.sales_orders LIMIT 5"
    },
]
# ChromaDB 저장: docs=["sales_orders: 고객사에 부품을 ..."], metas=[{"id":..., "columns":...}]

# data/entity_embeddings.py
ENTITY_DATA = [
    {"name": "삼성전기", "type": "manufacturer"},
    {"name": "LG이노텍", "type": "manufacturer"},
    {"name": "현대모비스", "type": "vendor"},
]
# ChromaDB 저장: docs=[회사명], metas=[{"name":..., "type":...}]
```

---

##  버전 히스토리

| 버전 | 날짜 | 주요 변경사항 |
|------|------|-------------|
| **1.0** | 2025-02-26 | 모놀리식 `api.py` (2346줄)  기능별 모듈화 구조 |
| **2.0** | 2025-02-27 | 학습 데이터 JSONL 수집  / 피드백 UI  자동 차트 생성  SQL SELECT/WITH 제한 제거 |
| **2.1** | 2025-03-01 | 대화 메모리 DB 영속화  이중 Y축 차트  다중 질문 LLM 분리  Cloudflare Tunnel 자동 시작  sqlglot AST 기반 컬럼 검증 강화 |

---

##  파일별 역할 한눈에 보기

| 파일 | 줄 수 | 핵심 역할 |
|------|-------|---------|
| [config.py](config.py) | 278 |  모든 설정 단일 관리 (LLMDBRAG캐시키워드비즈니스로직) |
| [app.py](app.py) | 849 | Streamlit UI + LangGraph 실행 + Plotly 차트 + 피드백 수집 |
| [db_init.py](db_init.py) | - | 앱 시작 시 DB 자동 초기화 및 상태 반환 |
| [models/llm_config.py](models/llm_config.py) | 173 | LLM 팩토리 패턴  싱글톤 캐시  LangSmith 자동 추적 |
| [models/vector_db.py](models/vector_db.py) | 275 | ChromaDB HTTP/로컬 연결  컬렉션 CRUD  Azure OpenAI 임베딩 |
| [sql/sql_validator.py](sql/sql_validator.py) | 353 | sqlglot AST 기반 7단계 SQL 검증 |
| [sql/sql_generator.py](sql/sql_generator.py) | - | LLM CTE SQL 생성  tenacity 재시도  오류 전략 분기 |
| [sql/sql_executor.py](sql/sql_executor.py) | 436 | SQLAlchemy 커넥션 풀  Cloudflare Tunnel 자동 시작  학습 로그 |
| [rag/retrievers.py](rag/retrievers.py) | 399 | 벡터+BM25 하이브리드  Cohere 리랭킹  3컬렉션 병렬 검색 |
| [agent/state.py](agent/state.py) | - | AgentState TypedDict 25개 필드 |
| [agent/nodes.py](agent/nodes.py) | 1018 | 7개 LangGraph 노드  다중 질문 분리  병렬 RAG+Context 로딩 |
| [cache/query_cache.py](cache/query_cache.py) | 280 | TTL 기반 QueryCache  RAGCache  MD5 정규화 키 |
| [memory/conversation_memory.py](memory/conversation_memory.py) | 627 | PostgreSQL 영속 대화  유사 질문 감지(cos)  아카이브 관리 |
| [log_config/logger_config.py](log_config/logger_config.py) | - | RotatingFileHandler + StreamHandler 설정 |
| [utils/helpers.py](utils/helpers.py) | 327 | 차트 추론  설명 생성  구조화 메모리  rapidfuzz 오타 보정 |
| [utils/training_logger.py](utils/training_logger.py) | 455 |  JSONL+DB 이중 학습 로그  최근 대화 조회 |
| [rag_project/rag_builder.py](../rag_project/rag_builder.py) | 232 | 4개 ChromaDB 컬렉션 빌드 CLI (--collections, --reset) |
