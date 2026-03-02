# llmServer/app/services/answer_service.py

import logging
from typing import Dict, List
from app.services.llm_service import LLMService


class AnswerService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate(self, state: Dict) -> Dict:
        """
        DB 실행 결과(rows)를 바탕으로 최종 자연어 답변 생성
        """
        intent = state.get("intent")
        question = state.get("refined_question") or state.get("question", "")

        # 1️⃣ [분기] 칫챗인 경우: 사장님 페르소나 전용 API 호출 (추후 확장)
        if intent == "CHIT_CHAT":
            # 칫챗용으로 별도 모델이나 프롬프트를 쓰고 싶다면 generate_router 등 활용 가능
            # 여기서는 우선 마커만 반환하거나 간단한 사장님 인사 생성
            return {
                "final_answer": await self.llm.generate_answer_chitchat(f"{question}")
            }

        # 2️⃣ [체크] DB 에러 발생 시
        db_res = state.get("db_result", "")
        if isinstance(db_res, str) and "Error" in db_res:
            return {"final_answer": f"❌ 데이터 조회 중 문제가 발생했습니다: {db_res}"}

        # 3️⃣ [체크] 데이터가 비어있는 경우
        rows = state.get("rows", [])
        if not rows:
            return {
                "final_answer": "🔍 조회된 데이터가 없습니다. 질문의 조건을 확인해 주세요."
            }

        # 4️⃣ [컨텍스트 빌딩] LLM에게 줄 '진실(Fact)' 데이터 조립
        # Record 객체를 dict로 변환하여 문자열화 (최대 20행으로 제한하여 토큰 절약)
        rows_formatted = "\n".join([str(dict(r)) for r in rows[:20]])

        # ExecuteDBService에서 넘겨준 메타데이터 활용
        meta = state.get("explain_meta", {})
        meta_str = (
            f"대상 테이블: {', '.join(meta.get('tables_used', []))}\n"
            f"수행된 집계: {', '.join(meta.get('aggregations', []))}\n"
            f"전체 결과 행 수: {meta.get('row_count', 0)}"
        )

        # 5️⃣ [LLM 호출] 시스템 프롬프트는 LLMService 내부에 Fix되어 있으므로 재료만 전달
        # 팩트(데이터)와 질문을 구분하여 전달
        final_prompt = (
            f"### 사용자 질문\n{question}\n\n"
            f"### DB 조회 데이터 (FACT)\n{rows_formatted}\n\n"
            f"### 데이터 정보\n{meta_str}"
        )

        try:
            # LLMService 내부의 generate_answer가 시스템 프롬프트를 붙여 실행함
            response = await self.llm.generate_answer(final_prompt)
            return {"final_answer": response}

        except Exception as e:
            logging.error(f"Answer generation failed: {repr(e)}")
            return {
                "final_answer": "죄송합니다. 답변 생성 중 기술적인 오류가 발생했습니다."
            }
