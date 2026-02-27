# llmServer/app/services/test/test_router_service_rule.py

# PYTHONPATH=. python -m app.services.test.test_router_service_rule

from app.services.router_service import RouterService


# 🔥 Mock LLMService (LLM 안 쓰게)
class MockLLMService:
    def generate_router(self, prompt: str):
        return "CHIT_CHAT"


def run_test():

    print("🚀 RouterService Rule 기반 테스트\n")

    router = RouterService(llm_service=MockLLMService())

    test_cases = [
        "이번달 매출 얼마야",
        "BCM5650 대체품 있어?",
        "안녕 오늘 뭐해",
    ]

    for q in test_cases:
        intent = router.route(q)
        print(f"질문: {q}")
        print(f"→ 분류: {intent}\n")


if __name__ == "__main__":
    run_test()