# llmServer/app/services/router_service.py

from app.services.llm_service import LLMService


class RouterService:

    DATA_KEYWORDS = [
        "재고",
        "품목",
        "제품",
        "상품",
        "부품",
        "수량",
        "매출",
        "매입",
        "판매",
        "구매",
        "많은",
        "적은",
        "최대",
        "최소",
        "평균",
        "합계",
        "얼마",
        "보여줘",
        "조회",
        "현황",
        "통계",
    ]

    TECH_SALES_KEYWORDS = [
        "스펙",
        "사양",
        "대체품",
        "호환",
        "납기",
        "리드타임",
        "EOL",
        "단종",
        "전압",
        "전류",
        "패키지",
    ]

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def route(self, question: str, work_context: str = "") -> str:
        # 디버깅용
        print("ROUTER INPUT:", question)

        # 1️⃣ rule 기반
        if any(kw in question for kw in self.DATA_KEYWORDS):
            # 디버깅용
            print("ROUTER RULE MATCHED: DATA_KEYWORDS")
            return "INVENTORY"

        if any(kw in question for kw in self.TECH_SALES_KEYWORDS):
            # 디버깅용
            print("ROUTER RULE MATCHED: TECH_SALES_KEYWORDS")
            return "TECH_SALES"

        # 2️⃣ LLM fallback
        prompt = self._build_prompt(question, work_context)

        try:
            raw = await self.llm_service.generate_router(prompt)
            # 디버깅용 프린트문
            print("DEBUG RAW:", raw)
            raw = raw.strip().upper()

            if "INVENTORY" in raw:
                return "INVENTORY"
            elif "TECH" in raw:
                return "TECH_SALES"
            return "CHIT_CHAT"

        except Exception:
            # 디버깅용
            print("예외 발생, LLM 라우터 실패. 기본값 INVENTORY로 라우팅")
            return "INVENTORY"

    def _build_prompt(self, question: str, ctx: str) -> str:
        ctx_section = f"[직전 업무 대화 맥락]\n{ctx}\n\n" if ctx else ""

        return f"""
        {ctx_section}
        질문: {question}

        반드시 아래 세 단어 중 하나만 출력하세요.
        다른 설명은 절대 붙이지 마세요.

        INVENTORY
        TECH_SALES
        CHIT_CHAT
        """
