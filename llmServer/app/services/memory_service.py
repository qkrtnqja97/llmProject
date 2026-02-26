# llmServer/app/services/memory_service.py

class MemoryService:

    PRONOUN_MAP = {
        "이 제품": "last_product",
        "해당 제품": "last_product",
        "그 제품": "last_product",
        "이 고객사": "last_vendor",
        "이 제조사": "last_manufacturer",
    }

    def inject(self, question: str, memory: dict) -> str:
        if not memory:
            return question

        refined = question

        for pronoun, key in self.PRONOUN_MAP.items():
            if pronoun in refined and memory.get(key):
                refined = refined.replace(pronoun, memory[key])

        return refined