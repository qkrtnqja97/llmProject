# llmServer/dev/run_router.py

from app.agent.nodes.router_node import RouterNode
from app.services.router_service import RouterService
from app.services.llm_service import LLMService


# -------------------------
# Fake LLM (Mock 대신 직접 구현)
# -------------------------
class FakeLLMService:
    def generate(self, prompt: str) -> str:
        if "재고" in prompt:
            return "sql"
        return "general"


def main():
    llm = FakeLLMService()
    llm = LLMService(llm_registry=None, prompt_registry=None)  # 실제 LLMService로 교체
    router_service = RouterService(llm)
    node = RouterNode(router_service)

    state = {"question": "재고 조회해줘"}
    result = node.run(state)

    print(result)


if __name__ == "__main__":
    main()
