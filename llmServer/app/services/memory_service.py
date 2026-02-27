# llmServer/app/services/memory_service.py


class MemoryService:

    PRONOUN_MAP = {
        "이 제품": "last_product",
        "해당 제품": "last_product",
        "그 제품": "last_product",
        "이 고객사": "last_vendor",
        "해당 고객사": "last_vendor",
        "이 제조사": "last_manufacturer",
        "해당 제조사": "last_manufacturer",
    }

    def inject(self, question: str, memory: dict | None) -> str:
        """
        대명사 / 생략 표현 보강
        """
        if not memory:
            return question

        q = question

        for pronoun, key in self.PRONOUN_MAP.items():
            if pronoun in q and memory.get(key):
                q = q.replace(pronoun, f"'{memory[key]}'")

        if "같은 기간" in q and memory.get("last_date_range"):
            q += f" (기간조건: {memory['last_date_range']})"

        return q

    def summarize_work_context(self, work_context: list[dict] | None) -> str:
        """
        라우터용 최근 대화 맥락 요약
        """
        if not work_context:
            return ""

        recent = work_context[-4:]
        lines = []

        for m in recent:
            role = "사용자" if m["role"] == "user" else "AI"
            lines.append(f"{role}: {m['content'][:80]}")

        return "\n".join(lines)
