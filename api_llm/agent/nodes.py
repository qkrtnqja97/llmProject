# -*- coding: utf-8 -*-
"""
에이전트 노드 구현
LangGraph 워크플로우의 각 처리 단계
"""

import re
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from api_llm.config import (
    DATA_KEYWORDS, TECH_SALES_KEYWORDS, SQL_CONFIG,
)
from api_llm.models import get_default_llm
from api_llm.sql import (
    clean_sql, validate_sql_syntax, validate_sql_static,
    get_retry_strategy, SQLGenerator, handle_follow_up_question,
    execute_sql, validate_result_dataframe,
)
from api_llm.rag import retrieve_parallel
from api_llm.utils import (
    StructuredMemory, correct_entity_typos, infer_chart_type,
    infer_chart_columns, is_chart_requested,
)

from .state import AgentState

logger = logging.getLogger(__name__)


# ==========================================
# 라우팅 헬퍼
# ==========================================

def split_multiple_questions(question: str, llm=None) -> List[str]:
    """
    질문 간 독립성을 판단하여 스마트 분리
    
    ✅ 분리하는 경우 (완전 독립적):
      - "월별 매출액을 알려주고 그래프로 나타내줘. 그리고 연도별 매출액을 그래프로 나타내줘"
      - "2024년 매출은? 2025년 비용은?" → 시간대가 다르면 분리
      - "A제품 재고는? B제품 가격은?" → 대상이 다르면 분리
    
    ❌ 유지하는 경우 (문맥 의존):
      - "2024년 분기별 매출은? 그리고 비용도 보여줘." → "비용"의 시간대가 암묵적
      - "년 매출은? 전년 대비 증감은?" → 두번째가 첫번째에 의존
    
    Args:
        question: 사용자 질문
        llm: LLM 인스턴스 (없으면 간단한 휴리스틱 사용)
    
    Returns:
        분리된 질문 리스트 (또는 원본)
    """
    import re
    
    # 1단계: 물음표/마침표로 문장 분리
    sentences = re.split(r'[.!?]+', question)
    raw_questions = [s.strip() for s in sentences if s.strip()]
    
    # 단일 질문 → 원본 반환
    if len(raw_questions) <= 1:
        return [question]
    
    # 2단계: 간단한 휴리스틱 (LLM 없을 때)
    if llm is None:
        # (1) 독립 질문 키워드 감지 ("그리고 ~ 을/를 그래프로" 패턴)
        # 예: "월별 매출을 알려주고 그래프로. 그리고 연도별 매출을 그래프로"
        independent_keywords = ["그리고", "그리고 또한", "또 다른", "추가로"]
        
        # 두 번째 이후 질문이 독립적 키워드로 시작 + 고유 시간/대상 포함
        is_independent = False
        if len(raw_questions) >= 2:
            second_q = raw_questions[1].lower()
            # "그리고 연도별", "그리고 월별", "그리고 분기별" 등
            time_keywords = ["연도별", "월별", "분기별", "일별", "주별", "년별"]
            if any(kw in second_q for kw in independent_keywords) and any(t in second_q for t in time_keywords):
                is_independent = True
                logger.info(f"📋 독립 질문 감지 (그리고 + 시간대) → 분리")
                return raw_questions
        
        # (2) 시간 조건 분리 ("2024년 ~ 2025년 ~" 형태)
        year_pattern = r'\d{4}년'
        years = set()
        for q in raw_questions:
            found_years = re.findall(year_pattern, q)
            years.update(found_years)
        
        if len(years) > 1:
            logger.info(f"📋 시간대 독립적 감지 (연도: {years}) → 분리")
            return raw_questions
        
        # (3) 제품명/실체 분리 ("A제품 ~, B제품 ~" 형태)
        entity_keywords = ["제품", "부품", "고객", "회사", "부서"]
        entities = []
        for q in raw_questions:
            for kw in entity_keywords:
                if kw in q:
                    # "A제품" 형태 추출
                    match = re.search(rf'(\S*){kw}', q)
                    if match:
                        entities.append(match.group(1) + kw)
        
        if len(set(entities)) > 1:
            logger.info(f"📋 실체 독립적 감지 ({set(entities)}) → 분리")
            return raw_questions
        
        # (4) 기본: 분리하지 않음 (문맥 유지)
        logger.info(f"📍 문맥 의존적 → 분리 안 함 (원본 유지)")
        return [question]
        
        # (3) 제품명/실체 분리 ("A제품 ~, B제품 ~" 형태)
        entity_keywords = ["제품", "부품", "고객", "회사", "부서"]
        entities = []
        for q in raw_questions:
            for kw in entity_keywords:
                if kw in q:
                    # "A제품" 형태 추출
                    match = re.search(rf'(\S*){kw}', q)
                    if match:
                        entities.append(match.group(1) + kw)
        
        if len(set(entities)) > 1:
            logger.info(f"📋 실체 독립적 감지 ({set(entities)}) → 분리")
            return raw_questions
        
        # (4) 기본: 문맥 유지 (분리 안 함)
        logger.info(f"📍 문맥 의존 강함 → 분리 안 함 (원본 유지)")
        return [question]
    
    # 3단계: LLM 기반 독립성 판단 (정확이지만 느림)
    split_prompt = PromptTemplate.from_template("""다음 질문들이 정말 독립적인지 판단하세요.

[질문 목록]
{questions_text}

[판단 기준]
- 독립적 (분리 권장): 시간대/대상/조건이 명확히 다름
- 의존적 (분리 금지): 대명사/생략된 조건으로 이전 질문에 의존
- 혼합: 일부는 의존, 일부는 독립 → "부분" 응답

[응답 형식]
독립: 모두 분리 가능
의존: 함께 처리해야 함
부분: Q1,Q2(의존) + Q3(독립)

응답:""")
    
    try:
        questions_text = "\n".join([f"Q{i+1}: {q}" for i, q in enumerate(raw_questions)])
        result = (split_prompt | llm | StrOutputParser()).invoke({
            "questions_text": questions_text
        }).strip().upper()
        
        if "독립" in result:
            logger.info(f"📋 LLM 분석: 독립적 → {len(raw_questions)}개 분리")
            return raw_questions
        else:
            logger.info(f"📍 LLM 분석: 의존적 → 분리 안 함")
            return [question]
    
    except Exception as e:
        logger.warning(f"LLM 독립성 판단 실패, 휴리스틱 사용: {e}")
        # 실패 시 휴리스틱으로 폴백
        return [question]


def is_data_question(q: str) -> bool:
    """데이터 관련 질문 판단"""
    return any(kw in q for kw in DATA_KEYWORDS)


def is_tech_sales(q: str) -> bool:
    """기술 영업 관련 질문 판단"""
    return any(kw in q for kw in TECH_SALES_KEYWORDS)


# ==========================================
# 1. 엔티티 링킹 노드 (질문 정제)
# ==========================================

def entity_linking_node(state: AgentState, entity_cache: Dict) -> Dict:
    """
    엔티티 링킹 및 질문 정제
    - 오타 보정 (벡터 기반 + rapidfuzz)
    - 동의어 감지
    - 대명사 해석 (대화 맥락 포함)
    """
    start_time = time.time()
    q = state.get("question", "")
    
    # 간단한 질문은 빠르게 처리 (숫자/날짜만 포함된 경우)
    import re
    simple_pattern = re.compile(r"^[0-9\-/\.\s가-힣]{1,20}$")  # 숫자, 날짜, 한글만
    if simple_pattern.match(q) and len(q) <= 15:
        logger.info(f"[Entity Linking 스킵] 간단한 질문: '{q}'")
        return {
            "refined_question": q,
            "synonym_hint": "",
            "error_history": [],
            "retry_count": 0,
            "result_anomalies": [],
            "validation_errors": [],
            "_timing_entity_linking": time.time() - start_time,
        }
    
    # 대화 맥락을 활용한 대명사 해석
    context = state.get("context", [])
    context_info = ""
    if context:
        # 대명사 관련 질문인지 확인
        pronoun_keywords = ["그거", "그것", "그거", "그따따", "그건", "그 중", "다시", "또", "이전", "같은"]
        has_pronoun = any(kw in q for kw in pronoun_keywords)
        
        if has_pronoun:
            context_lines = []
            for i, conv in enumerate(context, 1):
                question_text = conv.get("question", "").strip()
                if question_text:
                    context_lines.append(f"  {i}. {question_text}")
            
            if context_lines:
                context_info = "최근 대화: " + " | ".join([c.replace("  ", "").strip() for c in context_lines])
                logger.info(f"[대명사 감지] '{q}' → 맥락 활용: {context_info[:80]}")
    
    # 1차 오타 보정 (벡터 임베딩 포함)
    embeddings_data = entity_cache.get("embeddings_data")
    refined, synonym_hint = correct_entity_typos(
        q,
        entity_cache.get("manufacturers", []),
        entity_cache.get("vendors", []),
        embeddings_data=embeddings_data,  # ← 벡터 데이터 전달
    )
    
    # 2차 대명사 보완 (구조화 메모리 + 대화 맥락)
    memory = state.get("structured_memory", {})
    mem_obj = StructuredMemory()
    mem_obj.memory = memory
    refined = mem_obj.inject_to_question(refined)
    
    # 3차 대화 맥락 보완
    if context_info and "그" in q:
        refined = f"{refined} (참고: {context_info})"
    
    elapsed = time.time() - start_time
    logger.info(f"⏱️ [엔티티 링킹] {elapsed:.2f}초 | 질문 정제: '{q}' → '{refined}'")
    
    return {
        "refined_question": refined,
        "synonym_hint": synonym_hint,
        "error_history": [],
        "retry_count": 0,
        "result_anomalies": [],
        "validation_errors": [],
        "_timing_entity_linking": elapsed,
    }


# ==========================================
# 2. 라우터 노드 (의도 분류)
# ==========================================

def router_node(state: AgentState, llm=None) -> Dict:
    """
    사용자 질문 분류
    INVENTORY / TECH_SALES / CHIT_CHAT
    대화 맥락을 활용하여 "그거 다시" 같은 대명사 참조도 처리
    """
    start_time = time.time()
    llm = llm or get_default_llm()
    q = state.get("question", "")
    
    # 1차 키워드 기반
    if is_data_question(q):
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [라우터] {elapsed:.2f}초 | 키워드 매칭 → INVENTORY")
        return {"intent": "INVENTORY", "_timing_router": elapsed}
    
    if is_tech_sales(q):
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [라우터] {elapsed:.2f}초 | 키워드 매칭 → TECH_SALES")
        return {"intent": "TECH_SALES", "_timing_router": elapsed}
    
    # 2차 LLM 분류 (대화 맥락 포함)
    context = state.get("context", [])
    context_info = ""
    if context:
        context_lines = []
        for i, conv in enumerate(context, 1):
            question_text = conv.get("question", "").strip()
            if question_text:
                context_lines.append(f"  {i}. {question_text}")
        
        if context_lines:
            context_info = "\n[최근 대화 이력]\n" + "\n".join(context_lines)
    
    prompt = PromptTemplate.from_template("""당신은 전자부품 유통 회사의 분류기입니다.
질문을 다음 중 하나로 분류하세요:

INVENTORY  : 재고/매출/매입/수익 등 데이터 조회 또는 그에 대한 후속 질문
TECH_SALES : 부품 스펙, 대체품, 납기 등 기술 문의
CHIT_CHAT  : 일상 대화{context}

현재 질문: {q}
분류:""")
    
    try:
        invoke_dict = {"q": q, "context": context_info}
        raw = (prompt | llm | StrOutputParser()).invoke(invoke_dict).strip().upper()
        if "INVENTORY" in raw:
            result = "INVENTORY"
        elif "TECH_SALES" in raw or "TECH" in raw:
            result = "TECH_SALES"
        else:
            result = "CHIT_CHAT"
    except Exception:
        logger.exception("라우터 실패 → INVENTORY 폴백")
        result = "INVENTORY"
    
    elapsed = time.time() - start_time
    logger.info(f"⏱️ [라우터] {elapsed:.2f}초 | LLM 분류 → {result}")
    return {"intent": result, "_timing_router": elapsed}


# ==========================================
# 3. SQL 생성 노드
# ==========================================

def sql_generation_node(
    state: AgentState,
    llm=None,
    sql_generator: SQLGenerator = None,
    column_map: Dict = None,
    data_stats: Dict = None,
    entity_cache: Dict = None,
) -> Dict:
    """LLM 기반 SQL 생성 (RAG + Context 병렬 로딩)"""
    
    start_time = time.time()
    llm = llm or get_default_llm()
    column_map = column_map or {}
    data_stats = data_stats or {}
    
    q = state.get("refined_question", state.get("question", ""))
    error_history = state.get("error_history", [])
    
    # ──── 병렬 로딩: Context 구성 + RAG 검색 ────
    def load_context() -> str:
        """대화 맥락 구성"""
        context = state.get("context", [])
        work_context = ""
        if context:
            context_lines = []
            for i, conv in enumerate(context, 1):
                question_text = conv.get("question", "").strip()
                if question_text:
                    context_lines.append(f"  {i}. {question_text}")
            
            if context_lines:
                work_context = "[최근 대화 이력]\n사용자가 최근에 다음 주제들에 대해 문의했습니다:\n" + "\n".join(context_lines)
                logger.info(f"[대화 맥락 로드] {len(context_lines)}개 이전 질문")
        return work_context
    
    def load_schema() -> str:
        """스키마 정보 로드"""
        from api_llm.rag.retrievers import retrieve_schema
        schema_info = retrieve_schema(q, top_n=10)
        return schema_info
    
    def load_rag() -> str:
        """RAG 검색"""
        return retrieve_parallel(q)
    
    # 병렬 실행 (Context + Schema + RAG 동시)
    with ThreadPoolExecutor(max_workers=3) as executor:
        context_future = executor.submit(load_context)
        schema_future = executor.submit(load_schema)
        rag_future = executor.submit(load_rag)
        
        rag_start = time.time()
        try:
            work_context = context_future.result(timeout=10)
            schema_ctx = schema_future.result(timeout=10)
            rag_section = rag_future.result(timeout=10)
            rag_time = time.time() - rag_start
            logger.info(f"  ⏱️ [병렬 로딩] {rag_time:.2f}초 (Context + Schema + RAG 동시 실행)")
        except Exception as e:
            logger.warning(f"병렬 로딩 실패 → 순차 실행: {e}")
            work_context = load_context()
            schema_ctx = load_schema()
            rag_start = time.time()
            rag_section = load_rag()
            rag_time = time.time() - rag_start
    
    # SQLGenerator 생성 (스키마 정보 포함)
    sql_generator = SQLGenerator(llm=llm, schema_ctx=schema_ctx)
    
    # SQL 생성
    try:
        llm_start = time.time()
        sql = sql_generator.generate(
            question=q,
            data_stats=data_stats,
            rag_section=rag_section,
            work_context=work_context,
        )
        llm_time = time.time() - llm_start
        logger.info(f"  ⏱️ [LLM SQL 생성] {llm_time:.2f}초")
        
        # SQL 유효성 확인
        if not sql or sql.strip() == "":
            raise ValueError("LLM이 SQL을 생성하지 못했습니다")
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [SQL 생성] 전체 {elapsed:.2f}초 (병렬 로딩: {rag_time:.2f}초, LLM: {llm_time:.2f}초)")
        
        sql = clean_sql(sql)
        logger.info(f"[OK] SQL 생성 완료")
        
        return {
            "sql_query": sql,
            "_timing_sql_gen": elapsed,
            "_timing_rag": rag_time,
            "_timing_llm": llm_time,
        }
    
    except Exception as e:
        elapsed = time.time() - start_time
        error_str = str(e)
        
        # API 할당량 오류 구분
        if "할당량" in error_str or "quota" in error_str.lower() or "429" in error_str:
            logger.warning(f"[WARNING] LLM API 할당량 초과 ({elapsed:.2f}초)")
            error_msg = error_str  # sql_generator.py에서 제공하는 상세 메시지 사용
        else:
            logger.exception(f"[ERROR] SQL 생성 실패 ({elapsed:.2f}초)")
            error_msg = f"❌ SQL 생성 실패: {error_str[:150]}"
        
        return {
            "db_result": error_msg,
            "error_history": error_history + [error_str],
            "retry_count": state.get("retry_count", 0) + 1,
        }


# ==========================================
# 4. DB 실행 노드
# ==========================================

def db_execution_node(state: AgentState, column_map: Dict = None) -> Dict:
    """SQL 검증 및 실행"""
    
    start_time = time.time()
    sql = state.get("sql_query", "")
    column_map = column_map or {}
    error_history = state.get("error_history", [])
    
    # SQL 검증
    is_valid, reason = validate_sql_syntax(sql)
    if not is_valid:
        logger.warning(f"SQL 검증 실패: {reason}")
        retry_count = state.get("retry_count", 0) + 1
        new_error_history = [] if retry_count >= 2 else [reason]
        return {
            "db_result": f"❌ SQL 검증 실패: {reason}",
            "error_history": new_error_history,
            "retry_count": retry_count,
            "retry_strategy": "syntax",
        }
    
    # 정적 검증
    static_valid, static_reason, strategy = validate_sql_static(sql, column_map)
    if not static_valid:
        logger.warning(f"정적 검증 실패: {static_reason}")
        retry_count = state.get("retry_count", 0) + 1
        new_error_history = [] if retry_count >= 2 else [static_reason]
        return {
            "db_result": f"❌ {static_reason}",
            "validation_errors": [static_reason],
            "retry_strategy": strategy,
            "error_history": new_error_history,
            "retry_count": retry_count,
        }
    
    # SQL 실행
    try:
        question = state.get("question", "")
        schema_snapshot = str(state.get("schema_context", ""))[:500]
        
        exec_start = time.time()
        success, df, error_msg = execute_sql(
            sql,
            question=question,
            schema_snapshot=schema_snapshot,
            enable_training_log=True,
        )
        exec_time = time.time() - exec_start
        logger.info(f"  ⏱️ [DB 실행] {exec_time:.2f}초")
        
        if not success:
            logger.warning(f"쿼리 실행 실패: {error_msg}")
            retry_strategy = get_retry_strategy(error_msg, column_map)
            elapsed = time.time() - start_time
            retry_count = state.get("retry_count", 0) + 1
            new_error_history = [] if retry_count >= 2 else [error_msg]
            return {
                "db_result": f"❌ {error_msg[:200]}",
                "error_history": new_error_history,
                "retry_count": retry_count,
                "retry_strategy": retry_strategy.get("strategy", "unknown"),
                "_timing_db_exec": elapsed,
            }
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [DB 실행] 전체 {elapsed:.2f}초 | 결과 {len(df)}행")
        return {
            "df": df,
            "db_result": "SUCCESS",
            "retry_count": state.get("retry_count", 0),
            "_timing_db_exec": elapsed,
        }
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"쿼리 실행 오류 ({elapsed:.2f}초)")
        retry_count = state.get("retry_count", 0) + 1
        new_error_history = [] if retry_count >= 2 else [str(e)]
        return {
            "db_result": f"❌ {str(e)[:300]}",
            "error_history": new_error_history,
            "retry_count": retry_count,
            "_timing_db_exec": elapsed,
        }


# ==========================================
# 5. 결과 검증 노드
# ==========================================

def result_validation_node(state: AgentState, llm=None) -> Dict:
    """
    2단계 검증: 규칙 기반 필터(1단계) + 선택적 LLM(2단계)
    
    [1단계: 규칙 기반 필터 (객관적 이상)]
    ✅ 통과: NULL 비율 ≤ 50%, 데이터 타입 정상, 모든 값이 0/음수 아님
    ❌ 실패: 위 조건 위반 → 2단계로 진행
    
    [2단계: LLM 검증 (1단계 실패 시만)]
    - LLM에 의심 항목 설명하고 의미적 판단 요청
    - OK/WARN/REJECT 중 결정
    """
    start_time = time.time()
    llm = llm or get_default_llm()
    
    df = state.get("df")
    question = state.get("question", "")
    error_history = state.get("error_history", [])
    
    # 빈 결과는 정상 (데이터가 없는 것)
    if df is None or len(df) == 0:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [검증 1단계] {elapsed:.3f}초 | ✅ 결과 없음 (정상)")
        return {"result_anomalies": []}
    
    # ==========================================
    # 1단계: 규칙 기반 필터
    # ==========================================
    stage1_issues = []
    
    # 이슈 1: NULL 값 비율 > 50%
    for col in df.columns:
        null_ratio = df[col].isna().sum() / len(df)
        if null_ratio > 0.5:
            stage1_issues.append(f"[NULL 과다] {col}: {null_ratio*100:.0f}% NULL")
            logger.warning(f"  ⚠️ {col}: NULL 비율 {null_ratio*100:.0f}%")
    
    # 이슈 2: 숫자 컬럼이 모두 0 또는 음수
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        valid_values = df[col].dropna()
        if len(valid_values) > 0:
            if (valid_values <= 0).all():
                stage1_issues.append(f"[값 이상] {col}: 모든 값이 0 이상이 아님")
                logger.warning(f"  ⚠️ {col}: 모든 값이 ≤ 0")
    
    # 이슈 3: 데이터 타입 불일치 (숫자형으로 변환할 숫자 텍스트 감지)
    for col in df.select_dtypes(include=["object"]).columns:
        non_null_values = df[col].dropna().head(10)
        try:
            # 숫자처럼 보이는 텍스트가 많으면 타입 불일치 가능성
            numeric_like = sum(1 for v in non_null_values if isinstance(v, str) and v.replace(".", "").replace("-", "").isdigit())
            if len(non_null_values) > 0 and numeric_like / len(non_null_values) > 0.7:
                stage1_issues.append(f"[타입 불일치] {col}: 숫자처럼 보이는 텍스트")
                logger.warning(f"  ⚠️ {col}: 타입 불일치 의심")
        except:
            pass
    
    # ── 1단계 통과 판정 ──
    if not stage1_issues:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [검증 1단계] {elapsed:.3f}초 | ✅ 규칙 통과 (2단계 스킵)")
        return {"result_anomalies": [], "error_history": error_history}  # Self-Correction용 전달
    
    # ==========================================
    # 2단계: LLM 검증 (1단계 실패 시만)
    # ==========================================
    logger.info(f"⚠️ [검증 1단계 실패] {len(stage1_issues)}개 이슈 → 2단계 LLM 검증")
    
    # LLM에 의심 항목 요약
    issues_summary = "\n".join(stage1_issues)
    
    llm_prompt = PromptTemplate.from_template("""당신은 데이터 품질 검증 AI입니다.
SQL 쿼리 결과의 이상을 최종 판정하세요.

[사용자 질문]
{question}

[자동 감지된 이슈]
{issues}

[데이터 샘플 (최상단 5행)]
{sample}

[판정 기준]
OK     : 데이터가 정상. 이슈는 비즈니스 로직상 자연스러움
WARN   : 이상이 있지만 데이터는 신뢰할 수 있음. 사용자 검토 권유
REJECT : 데이터가 잘못되었거나 신뢰 불가능. 재쿼리 권장

[응답 형식 (한 줄)]
판정: OK|WARN|REJECT
이유: (15자 이내 간단 설명)""")
    
    try:
        llm_result = (llm_prompt | llm | StrOutputParser()).invoke({
            "question": question,
            "issues": issues_summary,
            "sample": df.head(5).to_string(),
        }).strip()
        
        # 판정 추출
        verdict = "REJECT"  # 기본: 이상 종료
        if "OK" in llm_result.upper():
            verdict = "OK"
        elif "WARN" in llm_result.upper():
            verdict = "WARN"
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [검증 2단계] {elapsed:.3f}초 | LLM 판정: {verdict}")
        logger.info(f"  {llm_result}")
        
        # OK/WARN은 통과, REJECT만 이상으로 반환
        if verdict in ["OK", "WARN"]:
            return {"result_anomalies": []}
        else:
            # Self-Correction: 검증 오류를 error_history에 추가하여 다음 재시도에서 모델이 참고
            feedback = f"[검증 피드백]\n{issues_summary}\n[데이터 샘플]\n{df.head(3).to_string()}"
            return {"result_anomalies": [f"LLM 검증 실패: {llm_result[:100]}"], "error_history": error_history + [feedback]}
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.warning(f"⏱️ [검증 2단계] {elapsed:.3f}초 | LLM 판정 오류 → 보수적 통과: {e}")
        # LLM 실패 시 데이터는 보여주되 주의 표시
        # Self-Correction: 1단계 이슈도 기록
        return {"result_anomalies": [], "error_history": error_history + stage1_issues}



# ==========================================
# 6. 시각화 노드
# ==========================================

def visualization_node(state: AgentState) -> Dict:
    """
    차트 타입 및 축 추론 (Dual Y-Axis 지원)
    - 키워드 기반 차트 종류 결정 (파이/막대/꺾은선/표)
    - DataFrame 컬럼 타입 분석 → x/y 축 자동 배정
    - 여러 y축 값의 스케일 차이 분석 → 필요시 secondary y축 추가
    """

    start_time = time.time()
    question = state.get("question", "")
    df: pd.DataFrame = state.get("df")

    # ── 1. 차트 요청 키워드 감지 ──────────────────────────
    CHART_KEYWORDS = {
        "bar":  ["막대", "bar", "바차트", "bar chart", "수직", "수평"],
        "line": ["꺾은선", "추이", "트렌드", "line", "선그래프", "변화"],
        "table": ["표", "테이블", "table", "목록"],
    }
    GENERAL_CHART_KEYWORDS = ["그래프", "차트", "chart", "graph", "시각화", "보여줘", "그려줘"]

    q_lower = question.lower()

    # 특정 차트 타입 키워드 매칭
    detected_type = None
    for chart_type, keywords in CHART_KEYWORDS.items():
        if any(kw in q_lower for kw in keywords):
            detected_type = chart_type
            break

    # 일반 차트 키워드만 있는 경우 → 데이터 형태로 자동 결정
    general_requested = any(kw in q_lower for kw in GENERAL_CHART_KEYWORDS)

    if detected_type is None and not general_requested:
        logger.info("시각화 요청 없음 → chart_info: none")
        return {"chart_info": {"type": "none"}}

    # ── 2. 데이터 유효성 확인 ────────────────────────────
    if df is None or df.empty or len(df.columns) < 1:
        logger.warning("시각화 요청이 있으나 DataFrame 없음")
        return {"chart_info": {"type": "none"}}

    # ── 3. x / y 축 컬럼 추론 ───────────────────────────
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    # 날짜·시간 컬럼 별도 추출 (꺾은선 우선 축 후보)
    # ✅ 단어 경계 기반 매칭 - "monthly_revenue" 같은 이름이 datetime으로 오분류되지 않도록
    _dt_pattern = re.compile(
        r'(?<![a-z])(date|year|month|day|일자|날짜|기간)(?![a-z])',
        re.IGNORECASE
    )
    # 한글 키워드는 별도 처리 (정규식 word boundary가 한글에 동작 안 함)
    _dt_hangul = ["일자", "날짜", "기간", "년도", "연도"]
    datetime_cols = [
        c for c in df.columns
        if pd.api.types.is_datetime64_any_dtype(df[c])
        or _dt_pattern.search(c)
        or any(kw in c for kw in ["월별", "연별", "분기별", "년월", "년도", "연도"])
        or any(kw in c for kw in _dt_hangul)
    ]
    
    # ✅ 우선순위: month > day > year (세분화된 시간 컬럼 우선)
    priority_order = ["month", "day", "date", "year", "일", "월", "년", "날짜"]
    datetime_cols_sorted = sorted(
        datetime_cols,
        key=lambda c: next((i for i, kw in enumerate(priority_order) if re.search(rf'(?<![a-z]){re.escape(kw)}(?![a-z])', c, re.IGNORECASE)), len(priority_order))
    )

    # x축: 정렬된 날짜 > 문자형 > 첫 번째 컬럼
    if datetime_cols_sorted:
        x_col = datetime_cols_sorted[0]  # ✅ month 우선
    elif non_numeric_cols:
        x_col = non_numeric_cols[0]
    else:
        x_col = df.columns[0]

    # y축: 숫자형 컬럼 중 x축 제외한 것 (단일이면 그것, 복수면 리스트)
    # ✅ datetime_cols도 제외 (sales_year/sales_month 같은 시간 컬럼이 Y축에 오면 안 됨)
    y_candidates = [c for c in numeric_cols if c != x_col and c not in datetime_cols]
    if not y_candidates:
        # fallback: x_col만 제외 완화하되, 전부 datetime 컬럼이면 차트 불가
        y_candidates_with_dt = [c for c in numeric_cols if c != x_col]
        if not y_candidates_with_dt or all(c in datetime_cols for c in y_candidates_with_dt):
            logger.warning("차트할 실질 값 컬럼 없음 (SQL 결과에 값 컬럼 미포함) → chart_info: none")
            return {"chart_info": {"type": "none"}}
        y_candidates = y_candidates_with_dt
    if not y_candidates and numeric_cols:
        # 최후 fallback: 컬럼이 1개뿐인 경우
        y_candidates = [numeric_cols[0]]

    y_col = y_candidates[0] if len(y_candidates) == 1 else y_candidates  # 복수 허용

    # ── 4. 차트 타입 자동 결정 (일반 요청인 경우) ────────
    if detected_type is None:
        row_count = len(df)
        
        # 시간 관련 키워드
        time_keywords = ["월별", "분기별", "연도별", "일별", "주별", "시간대", "기간", "추이", "변화", "흐름", "트렌드", "증감"]
        has_time_keyword = any(kw in q_lower for kw in time_keywords)
        
        # 수치 비교 키워드 (파이보다 막대/꺾은선이 나음)
        comparison_keywords = ["판매", "매출", "비용", "수량", "제품", "top", "평균", "합계", "개수", "비교", "순위", "차이", "대비"]
        has_comparison_keyword = any(kw in q_lower for kw in comparison_keywords)
        
        # 결정 로직
        # 1. 시간 키워드 있음 → 시간 서열에 따라 막대/꺾은선
        if has_time_keyword:
            if any(kw in q_lower for kw in ["추이", "변화", "증감", "트렌드"]):
                detected_type = "line"  # 변화 추세 → 꺾은선
            else:
                detected_type = "bar"  # 시간별 비교 → 막대
        # 3. 수치 비교 키워드 → 막대 우선
        elif has_comparison_keyword:
            detected_type = "bar"
        # 4. 시계열 데이터만 있음 → 꺾은선
        elif datetime_cols:
            detected_type = "line"
        # 5. 데이터 적으면 → 카테고리 표시 (표)
        elif row_count <= 3:
            detected_type = "table"
        # 6. 기본 → 막대
        else:
            detected_type = "bar"

    # ── 5. 다중 Y축 분석 (Dual Y-Axis) ──────────────────────
    use_secondary_axis = False
    y_axes = {}
    
    if isinstance(y_col, list) and len(y_col) > 1 and detected_type in ["bar", "line"]:
        # 여러 y값이 있는 경우 스케일 차이 분석
        # ✅ x축/datetime 컬럼이 y_col에 섞였으면 먼저 제거
        y_col = [c for c in y_col if c != x_col and c not in datetime_cols]
        if len(y_col) == 0:
            y_col = y_candidates[0] if y_candidates else df.columns[-1]
        # 1개로 줄어든 경우 → 단일 컬럼으로 확정, Dual Axis 스킵
        if isinstance(y_col, list) and len(y_col) == 1:
            y_col = y_col[0]

        # 여전히 복수 컬럼인 경우에만 스케일 분석 → Dual Y-Axis 결정
        if isinstance(y_col, list) and len(y_col) > 1:
            try:
                scales = {}
                for col in y_col:
                    if col in df.columns:
                        non_null = df[col].dropna()
                        if len(non_null) > 0:
                            min_val = non_null.min()
                            max_val = non_null.max()
                            if min_val != 0:
                                scale_ratio = max_val / min_val if min_val > 0 else max_val - min_val
                            else:
                                scale_ratio = max_val if max_val != 0 else 1
                            scales[col] = {
                                "min": min_val,
                                "max": max_val,
                                "range": max_val - min_val,
                                "ratio": scale_ratio,
                            }

                if len(scales) >= 2:
                    max_range = max(s["range"] for s in scales.values())
                    min_range = min(s["range"] for s in scales.values())
                    if max_range > 0 and min_range > 0:
                        range_ratio = max_range / min_range
                        if range_ratio > 10:
                            use_secondary_axis = True
                            logger.info(f"📊 스케일 차이 감지 ({range_ratio:.1f}배) → Dual Y-Axis 사용")
                            sorted_cols = sorted(scales.items(), key=lambda x: x[1]["range"], reverse=True)
                            for i, (col, _) in enumerate(sorted_cols):
                                y_axes[col] = "primary" if i == 0 else "secondary"

            except Exception as e:
                logger.warning(f"스케일 분석 실패: {e}")
                for col in y_col:
                    y_axes[col] = "primary"

    # ── 6. DataFrame → Recharts 호환 data 배열 직렬화 ──────
    # NaN → None 변환 (JSON 직렬화 호환)
    data_records = df.where(pd.notnull(df), None).to_dict("records")

    # dataKeys: y축 컬럼 목록 (항상 리스트)
    data_keys = [y_col] if isinstance(y_col, str) else list(y_col)

    chart_info = {
        # ── 공통 ────────────────────────────────────────────────
        "type": detected_type,           # "bar" | "line" | "table" | "none"
        "title": question if len(question) <= 80 else question[:77] + "...",

        # ── Recharts 키 (프론트엔드 React에서 그대로 사용 가능) ──
        "xKey": x_col,                   # <XAxis dataKey="xKey">
        "dataKeys": data_keys,           # [<Bar dataKey="..."> ...]
        "useSecondaryAxis": use_secondary_axis,  # ComposedChart dual axis 여부
        "yAxes": y_axes,                 # {"col": "primary" | "secondary"}
        "data": data_records,            # Recharts data prop에 직접 전달
    }

    elapsed = time.time() - start_time
    axis_info = " (Dual Axis)" if use_secondary_axis else ""
    logger.info(f"⏱️ [시각화] {elapsed:.2f}초 | 📊 차트 결정: type={detected_type}{axis_info}")
    return {"chart_info": chart_info, "_timing_visual": elapsed}



# ==========================================
# 7. 답변 생성 노드
# ==========================================

def answer_node(state: AgentState, llm=None) -> Dict:
    """최종 답변 생성 (대화 맥락 포함)"""
    
    start_time = time.time()
    llm = llm or get_default_llm()
    intent = state.get("intent", "INVENTORY")
    
    # CHIT_CHAT 처리
    if intent == "CHIT_CHAT":
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [답변] {elapsed:.2f}초 | CHIT_CHAT 응답")
        return {"db_result": "업무와 관련된 질문을 해주세요.", "_timing_answer": elapsed, "error_history": []}
    
    # TECH_SALES 처리
    if intent == "TECH_SALES":
        q = state.get("question", "")
        prompt = PromptTemplate.from_template("""당신은 전자부품 수입 유통 전문 AI입니다.
기술 문의에 전문적으로 답변하세요:

[질문]
{q}

[답변]""")
        try:
            ans = (prompt | llm | StrOutputParser()).invoke({"q": q})
            elapsed = time.time() - start_time
            logger.info(f"⏱️ [답변] {elapsed:.2f}초 | TECH_SALES 답변 생성")
            return {"db_result": ans, "_timing_answer": elapsed, "error_history": []}
        except Exception:
            elapsed = time.time() - start_time
            logger.exception(f"⏱️ [답변] {elapsed:.2f}초 | TECH_SALES 처리 실패")
            return {"db_result": "기술 문의 처리 중 오류가 발생했습니다.", "_timing_answer": elapsed, "error_history": []}
    
    # INVENTORY 처리
    db_res = state.get("db_result", "")
    if "Error" in db_res or "❌" in db_res:
        elapsed = time.time() - start_time
        return {"db_result": f"분석 삭제: {db_res}", "_timing_answer": elapsed, "error_history": []}
    
    df = state.get("df")
    if df is None or df.empty:
        elapsed = time.time() - start_time
        return {"db_result": "해당 조건의 데이터가 존재하지 않습니다.", "_timing_answer": elapsed, "error_history": []}
    
    # 대화 맥락 구성
    context = state.get("context", [])
    context_info = ""
    if context:
        context_lines = []
        for i, conv in enumerate(context, 1):
            question_text = conv.get("question", "").strip()
            if question_text:
                context_lines.append(f"  {i}. {question_text}")
        
        if context_lines:
            context_info = "\n[최근 분석 이력]\n사용자가 최근에 다음 주제들을 분석했습니다:\n" + "\n".join(context_lines)
            context_info += "\n현재 분석이 이전 분석과 연관이 있을 경우, 비교 분석 또는 추가 인사이트를 제공하세요."
    
    # 데이터 기반 답변
    prompt = PromptTemplate.from_template("""당신은 스마트 기업 데이터 분석 비서입니다.
아래 [분석 결과 데이터]를 바탕으로 사용자에게 전문적인 답변을 제공하십시오.

[사용자 질문]
{q}{context}

[분석 결과 데이터]
{d}

[답변 가이드]
1. 결과 해석: 데이터의 수치를 단순히 나열하지 말고 질문 의도에 맞게 설명하십시오.
2. 데이터 완전성: 제공된 데이터의 모든 행(월, 기간, 항목 등)을 빠짐없이 다루십시오. 일부만 언급하거나 중간에 생략하지 마십시오.
3. 상황별 대응:
   - 데이터가 있을 경우: 결론부터 제시하고 수치적 근거를 설명하십시오.
   - 데이터가 없을 경우: 요청 조건에 맞는 기록이 없음을 명확히 알리고 그 이유를 정중히 설명하십시오.
4. 인사이트 제공: 데이터 관계를 분석하여 유용한 인사이트를 덧붙이십시오.
5. 태도: 전문 비서처럼 정중하고 신뢰감 있는 말투를 유지하십시오.

[답변]""")

    try:
        ans = (prompt | llm | StrOutputParser()).invoke({
            "q": state.get("question", ""),
            "d": df.head(200).to_string() if len(df) > 200 else df.to_string(),
            "context": context_info,
        })
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [답변] {elapsed:.2f}초 | INVENTORY 답변 생성")        
        # 대화 기록 저장 (성공한 최종 답변)
        try:
            from api_llm.utils.training_logger import save_conversation
            save_conversation(
                question=state.get("question", ""),
                response_summary=ans[:200],  # 답변 요약
                refined_question=state.get("refined_question"),
                sql_query=state.get("sql_query"),
            )
        except Exception as log_err:
            logger.warning(f"⚠️ 대화 저장 실패: {str(log_err)[:100]}")
        
        return {"db_result": ans, "_timing_answer": elapsed, "error_history": []}
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"⏱️ [답변] {elapsed:.2f}초 | 답변 생성 실패")
        return {"db_result": f"답변 생성 중 오류: {str(e)[:100]}", "_timing_answer": elapsed, "error_history": []}


# ==========================================
# 조건부 라우팅 함수
# ==========================================

def should_retry(state: AgentState) -> str:
    """재시도 판단"""
    has_error = "Error" in state.get("db_result", "") or "❌" in state.get("db_result", "")
    under_limit = state.get("retry_count", 0) < SQL_CONFIG["MAX_RETRY_COUNT"]
    
    if has_error and under_limit:
        return "retry"
    return "success"


def should_retry_result(state: AgentState) -> str:
    """결과 이상 재시도 판단"""
    if state.get("result_anomalies") and state.get("retry_count", 0) < SQL_CONFIG["MAX_RETRY_COUNT"]:
        return "retry"
    return "visual"


def route_by_intent(state: AgentState) -> str:
    """의도별 라우팅"""
    intent = state.get("intent", "INVENTORY")
    if intent in ("CHIT_CHAT", "TECH_SALES"):
        return "answer"
    return "sql_gen"
