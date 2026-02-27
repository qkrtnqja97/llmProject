# llmServer/app/agent/nodes/refine_node.py

# from app.agent.graph import AgentState

from app.services.entity_service import EntityResolverService
from app.services.memory_service import MemoryService


class RefineNode:

    def __init__(
        self,
        entity_service: EntityResolverService,
        memory_service: MemoryService,
    ):
        self.entity_service = entity_service
        self.memory_service = memory_service

    def __call__(self, state: dict):

        question = state["question"]

        # refined : 오타 보정 & part_number 보정
        # synonym_hint : 동의어 힌트
        result = self.entity_service.resolve(question)

        refined = result["refined_question"]
        synonym_hint = result["synonym_hint"]

        # 구조화 메모리 주입
        memory = state.get("structured_memory", {})
        refined = self.memory_service.inject(refined, memory)

        return {
            "refined_question": refined,
            "synonym_hint": synonym_hint,
            "error_history": [],
            "retry_count": 0,
            "result_anomalies": [],
            "validation_errors": [],
        }
