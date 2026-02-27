# llmServer/app/services/router_service.py

class RouterService:

    DATA_KEYWORDS = [
        "재고", "품목", "제품", "상품", "부품", "수량",
        "매출", "매입", "판매", "구매",
        "많은", "적은", "최대", "최소", "평균", "합계",
        "얼마", "보여줘", "조회", "현황", "통계",
    ]

    TECH_SALES_KEYWORDS = [
        "스펙", "사양", "대체품", "호환",
        "납기", "리드타임", "EOL", "단종",
        "전압", "전류", "패키지",
    ]

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def route(self, question: str, work_context: str = "") -> str:

        # 1️⃣ rule 기반
        if any(kw in question for kw in self.DATA_KEYWORDS):
            return "INVENTORY"

        if any(kw in question for kw in self.TECH_SALES_KEYWORDS):
            return "TECH_SALES"

        # 2️⃣ LLM fallback
        prompt = self._build_prompt(question, work_context)

        try:
            raw = self.llm_service.generate_router(prompt).strip().upper()

            if "INVENTORY" in raw:
                return "INVENTORY"
            elif "TECH" in raw:
                return "TECH_SALES"
            return "CHIT_CHAT"

        except Exception:
            return "INVENTORY"

    def _build_prompt(self, question: str, ctx: str) -> str:
        ctx_section = f"[직전 업무 대화 맥락]\n{ctx}\n\n" if ctx else ""

        return f"""
          {ctx_section}
          질문: {question}

          분류:
          """