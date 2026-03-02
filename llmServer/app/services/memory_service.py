# app/services/memory_service.py

import re
import logging
from typing import  Dict, Optional, List
from app.infra.database.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)

class MemoryService:

    def __init__(self, conversation_repository):
        self.conversation_repository = conversation_repository

    # --------------------------------------------------
    # 최근 대화 조회
    # --------------------------------------------------
    async def load_recent(self, user_id: str, limit: int = 6):
        rows = await self.conversation_repository.get_recent(
            user_id=user_id,
            limit=limit,
        )
        return list(reversed(rows))  # 시간순 정렬

    # --------------------------------------------------
    # 통합 메모리 처리
    # --------------------------------------------------
    async def inject_context(self, user_id: str, question: str):

        recent = await self.load_recent(user_id)

        # 1️⃣ follow-up 재조립
        rebuilt_q = self._rebuild_followup(question, recent)

        # 2️⃣ structured memory 추출
        structured_memory = self._extract_structured_memory(recent)

        return rebuilt_q, structured_memory

    # --------------------------------------------------
    # follow-up 재조립
    # --------------------------------------------------
    def _rebuild_followup(self, question: str, recent: List[Dict]) -> str:

        if not recent:
            return question

        q = question.strip()

        if len(q.replace(" ", "")) > 12:
            return q

        base_q = self._find_base_question(recent, q)
        if not base_q:
            return q

        # 🔥 연도 치환
        year_match = re.search(r'(\d{2,4})년', q)
        if year_match:
            new_year = year_match.group(1)
            if len(new_year) == 2:
                new_year = f"20{new_year}"

            rebuilt = re.sub(r'\d{2,4}년', f"{new_year[-2:]}년", base_q)
            logger.info(f"[연도치환] {q} → {rebuilt}")
            return rebuilt

        # 🔥 분기 치환
        qtr_match = re.search(r'([1-4])분기', q)
        if qtr_match:
            qtr = qtr_match.group(1)

            if "분기" in base_q:
                rebuilt = re.sub(r'[1-4]분기', f"{qtr}분기", base_q)
            else:
                rebuilt = base_q + f" ({qtr}분기 기준)"

            logger.info(f"[분기치환] {q} → {rebuilt}")
            return rebuilt

        return q

    # --------------------------------------------------
    # 기준 질문 찾기 (핵심 수정)
    # --------------------------------------------------
    def _find_base_question(self, recent: List[Dict], question: str):

        # 연도 질문
        if re.search(r'\d{2,4}년', question):
            for m in reversed(recent):
                if re.search(r'\d{2,4}년', m["question"]):
                    return m["question"]

        # 분기 질문
        if re.search(r'[1-4]분기', question):
            for m in reversed(recent):
                if "분기" in m["question"]:
                    return m["question"]

        # fallback: 가장 최근 질문
        return recent[-1]["question"] if recent else ""
      
    # -----------------------------------
    # 저장
    # -----------------------------------
    async def save_conversation(
        self,
        user_id: str,
        session_id: str,
        question: str,
        refined_question: str,
        response_data: Dict,
        final_sql: Optional[str],
        entity_corrections: Dict,
        execution_time_ms: int,
    ):
        await self.conversation_repository.save(
            user_id=user_id,
            session_id=session_id,
            question=question,
            refined_question=refined_question,
            response_data=response_data,
            final_sql=final_sql,
            entity_corrections=entity_corrections,
            execution_time_ms=execution_time_ms,
        )
        
    # --------------------------------------------------
    # structured memory 추출
    # --------------------------------------------------
    def _extract_structured_memory(self, recent: List[Dict]) -> Dict:

        memory = {}

        for m in reversed(recent):

            text_blob = ""
            if m.get("response_data"):
                text_blob = str(m["response_data"])

            # 🔥 제품코드 추출
            pn_matches = re.findall(r'\b[A-Z0-9][A-Z0-9\-#\.+]{4,}\b', text_blob)
            if pn_matches and "last_product" not in memory:
                memory["last_product"] = pn_matches[-1]

            # 🔥 연도 범위 추출
            year_match = re.search(r'\d{4}', m["question"])
            if year_match and "last_year" not in memory:
                memory["last_year"] = year_match.group(0)

        return memory