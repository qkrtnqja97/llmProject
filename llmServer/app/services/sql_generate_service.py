# app/services/sql_generate_service.py

import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class SQLGenerateService:

    def __init__(
        self,
        llm_service,
        retry_service,
        rag_service,
        schema_provider,
        data_stats_provider,
    ):
        self.llm_service = llm_service
        self.retry_service = retry_service
        self.rag_service = rag_service
        self.schema_provider = schema_provider
        self.data_stats_provider = data_stats_provider

    # ─────────────────────────────
    # 메인 실행
    # ─────────────────────────────
    async def generate(self, state: Dict) -> Dict:

        question = state["refined_question"]
        error_history = state.get("error_history", [])
        synonym_hint = state.get("synonym_hint", "")
        last_error = error_history[-1] if error_history else ""

        # 1️⃣ Retry 전략 분석
        retry_section = ""
        if last_error:
            retry_info = self.retry_service.analyze(last_error)

            if retry_info.get("hint"):
                retry_section = f"""
                    [이전 SQL 실행 실패]

                    에러:
                    {last_error}

                    아래 전략을 반드시 반영하여 SQL을 수정하시오.
                    같은 실수를 반복하지 말 것.

                    수정 지침:
                    {retry_info['hint']}
                    """

        # 2️⃣ RAG 병렬 구성
        rag_section = await self.rag_service.build(
            question=question,
            synonym_hint=synonym_hint,
            last_error=last_error,
        )

        # 3️⃣ 스키마 + 데이터 기간
        schema_ctx = self.schema_provider.get_schema()
        min_date, max_date = self.data_stats_provider.get_range()

        # 4️⃣ 프롬프트 구성
        user_prompt = self._build_user_prompt(
            question=question,
            schema=schema_ctx,
            min_date=min_date,
            max_date=max_date,
            error_history=error_history,
            retry_section=retry_section,
            rag_section=rag_section,
        )

        # 5️⃣ LLM 호출
        raw_sql = await self.llm_service.generate_sql(user_prompt)

        # 6️⃣ SQL 정리
        sql = self._clean_sql(raw_sql)

        # 7️⃣ SQL 기본 검증 (안전장치)
        if not self._is_valid_select(sql):
            logger.warning("⚠️ 유효하지 않은 SQL 반환")
            return {
                "sql_query": "",
                "error": "invalid_sql_generated"
            }

        logger.info(f"\n📌 생성된 SQL:\n{sql}")

        return {"sql_query": sql}

    # ─────────────────────────────
    # Prompt Builder
    # ─────────────────────────────
    def _build_user_prompt(
        self,
        question,
        schema,
        min_date,
        max_date,
        error_history,
        retry_section,
        rag_section,
    ) -> str:

        return f"""
          [스키마 정보]
          {schema}

          [데이터 유효 기간]
          {min_date} ~ {max_date}

          [이전 에러 기록]
          {error_history}

          {retry_section}

          {rag_section}

          [사용자 질문]
          {question}

          반드시 실행 가능한 PostgreSQL SELECT 문만 생성하라.
          INSERT, UPDATE, DELETE 금지.
          설명 금지.
          마크다운 금지.
          SQL 한 개만 출력하라.
          """

    # ─────────────────────────────
    # SQL 클린업
    # ─────────────────────────────
    def _clean_sql(self, raw: str) -> str:

        if not raw:
            return ""

        # ANSI escape 제거
        raw = re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', raw)

        # 코드블럭 추출
        match = re.search(
            r'```(?:sql)?\s*(.*?)\s*```',
            raw,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            sql = match.group(1).strip()
        else:
            sql = raw.strip()

        # 세미콜론 이후 제거
        sql = sql.split(";")[0].strip()

        return sql

    # ─────────────────────────────
    # SQL 유효성 최소 검증
    # ─────────────────────────────
    def _is_valid_select(self, sql: str) -> bool:

        if not sql:
            return False

        sql_lower = sql.lower().strip()

        # SELECT 시작 확인
        if not sql_lower.startswith("select"):
            return False

        # 위험 쿼리 차단
        forbidden = ["insert ", "update ", "delete ", "drop ", "alter "]
        if any(word in sql_lower for word in forbidden):
            return False

        return True