# -*- coding: utf-8 -*-
"""
SQL 생성 모듈
- LLM 기반 SQL 생성
- 후속자 처리 및 프롬프트 엔지니어링
- RAG 통합
"""

import re
import logging
import time
from typing import Dict, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from api_llm.config import SQL_CONFIG, DATABASE_CONFIG, BUSINESS_LOGIC
from api_llm.models import get_default_llm

logger = logging.getLogger(__name__)


class SQLGenerator:
    """LLM 기반 SQL 생성기"""

    def __init__(self, llm=None, schema_ctx: str = "", column_map: dict = None):
        self.llm = llm or get_default_llm()
        self.schema_ctx = schema_ctx
        self.column_map = column_map or {}

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _generate_with_retry(self, prompt, ctx):
        """재시도 로직을 포함한 LLM 호출"""
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke(ctx)
        
        # 빈 응답 감지
        if not response or response.strip() == "":
            raise ValueError("LLM이 빈 응답을 반환했습니다.")
        
        return response

    def generate(
        self,
        question: str,
        data_stats: Dict = None,
        rag_section: str = "",
        work_context: str = "",
    ) -> str:
        """
        LLM으로부터 SQL 생성
        
        Args:
            question: 사용자 질문
            data_stats: {'min_date': '', 'max_date': ''}
            rag_section: RAG 검색 결과
            work_context: 업무 맥락
        
        Returns:
            생성된 SQL 쿼리
        """
        
        data_stats = data_stats or {"min_date": "", "max_date": ""}

        prompt = PromptTemplate.from_template("""당신은 기업 데이터 분석을 위한 PostgreSQL 전문가입니다.
다음 [스키마 명세]를 철저히 준수하여 SQL을 작성하십시오.

[스키마 명세]
{schema}
데이터 기간: {min_date} ~ {max_date}

[사용 가능한 스키마]
- inventory_mgmt: 모든 데이터 테이블 사용 가능

[SQL 작성 및 보안 규칙 (엄격 준수)]
1. 정보 참조 원칙:
   - 반드시 위 [스키마 명제]에 나열된 테이블 정보, PK, FK, Column, 그리고 조인 관계를 근거로만 쿼리를 작성하십시오.
   - 명세서에 기술되지 않은 컬럼이나 테이블을 추측하여 사용하는 것은 절대 금지합니다.

2. 조인(JOIN) 및 중복 방지:
   - 테이블 간 직접적인 대량 조인은 데이터 중복(Cartesian Product)을 유발하므로 금지합니다.
   - 각 테이블은 별도의 CTE에서 먼저 필요한 만큼 필터링 및 집계(SUM)를 수행한 후, 마지막에 조인하십시오.

3. 일반화된 쿼리 작성 규칙 (분석 로직):
   - 안전한 집계: 모든 집계 함수(SUM, COUNT 등) 결과에는 항상 COALESCE(..., 0)을 적용하십시오.
   - 단계적 CTE 구조: '데이터 조회(Lookups)', '집계(Aggregations)', '최종 계산(Calculations)'으로 논리적으로 분리하십시오.
   - 데이터 타입 명시: 산술 연산 시 필요하다면 CAST(val AS NUMERIC)를 사용하십시오.
   - 날짜 월별 집계: 월별 집계 시 반드시 DATE_TRUNC('month', date_col) 또는 TO_CHAR(DATE_TRUNC('month', date_col), 'YYYY-MM') 패턴을 사용하십시오. EXTRACT()로 year/month를 분리한 뒤 MAKE_DATE()로 재조합하는 패턴은 절대 금지입니다 (EXTRACT 반환 타입이 numeric이라 MAKE_DATE integer 인자와 충돌함).
   - 조회 전용: 데이터 변경은 금지하며 모든 테이블 앞에는 스키마명을 붙이십시오 (inventory_mgmt.*)
   - 방어적 SQL: 예외 상황을 고려하여 SQL 내에서 루프(WITH RECURSIVE 등)나 조건문(CASE)을 활용하십시오.
   - 제품 식별 강화: 분석 보고 시 제품을 지칭하는 결과값에는 'description'(카테고리)뿐만 아니라, 반드시 'part_number'(고유 번호)를 함께 포함하여 조회하십시오.

4. 출력 형식:
   - 복합적인 분석은 WITH 구문(CTE)으로 단계를 나누어 작성하십시오.
   - 오직 SQL 쿼리만 출력하십시오.

[질문]
{q}{ctx}{rag}

SQL:""")
        
        # 입력값 구성
        ctx_input = f"\n[업무 맥락]\n{work_context}" if work_context else ""
        rag = f"\n[RAG]\n{rag_section}" if rag_section else ""
        
        try:
            invoke_dict = {
                "schema": self.schema_ctx,
                "min_date": data_stats.get("min_date", ""),
                "max_date": data_stats.get("max_date", ""),
                "q": question,
                "ctx": ctx_input,
                "rag": rag,
            }
            
            # 재시도 로직 포함 LLM 호출
            sql = self._generate_with_retry(prompt, invoke_dict)
            
            if not sql or sql.strip() == "":
                raise ValueError("LLM이 빈 응답을 반환했습니다. API 할당량을 확인하세요.")
            
            logger.info(f"[OK] SQL 생성 완료")
            return sql
        
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg or "rate" in error_msg.lower():
                logger.error(f"[ERROR] Google Gemini API 할당량 초과. 나중에 다시 시도하세요.")
                raise ValueError(
                    "⚠️ LLM API 할당량 초과\n"
                    "\n[원인]\n"
                    "- Google Gemini Free Tier: 20회/일 제한\n"
                    "- 계정의 모든 API 키가 할당량 공유\n"
                    "\n[해결 방법]\n"
                    "1. 내일 자정(UTC)에 자동 리셋\n"
                    "2. 유료 계획으로 업그레이드\n"
                    "3. 캐시된 응답 사용 (이전 질문 반복)"
                )
            logger.exception("SQL 생성 중 오류")
            raise


def handle_follow_up_question(prev_sql: str, follow_up: str) -> str:
    """후속 질문 처리"""
    return f"{prev_sql}\n-- 후속: {follow_up}"


def inject_memory_to_question(question: str, memory: Dict) -> str:
    """메모리를 질문에 주입"""
    return question