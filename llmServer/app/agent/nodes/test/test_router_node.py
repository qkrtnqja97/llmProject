# app/agent/nodes/test/test_router_node.py
# PYTHONPATH=. python -m app.agent.nodes.test.test_router_node

from app.agent.nodes.router_node import RouterNode
from app.services.router_service import RouterService


# -------------------------
# Fake LLM (Mock 대신 직접 구현)
# -------------------------
class FakeLLMService:
    def generate(self, prompt: str) -> str:
        if "재고" in prompt:
            return "sql"
        return "general"


# -------------------------
# Test Case
# -------------------------
def test_router_node_sql_intent():
    # Arrange (객체 조립)
    fake_llm = FakeLLMService()
    router_service = RouterService(fake_llm)
    router_node = RouterNode(router_service)

    state = {"question": "재고 조회해줘"}

    # Act
    result = router_node.run(state)

    # Assert
    assert result["intent"] == "sql"


def test_router_node_general_intent():
    fake_llm = FakeLLMService()
    router_service = RouterService(fake_llm)
    router_node = RouterNode(router_service)

    state = {"question": "오늘 날씨 어때?"}

    result = router_node.run(state)

    assert result["intent"] == "general"
