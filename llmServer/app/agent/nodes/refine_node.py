# llmServer/app/agent/nodes/refine_node.py

from llmServer.app.agent.graph import AgentState
from app.services.entity.entity_service import EntityResolverService

def entity_linking_node(
    state: AgentState,
    entity_service: EntityResolverService,
    memory_service,
):

    question = state["question"]
    
    # 1. 오타 보정
    # 2. part_number 보정
    # 3. 동의어 힌트
    refined, synonym_hint = entity_service.resolve(question)
  

    # 4. 구조화 메모리 주입
    memory = state.get("structured_memory", {})
    refined = memory_service.inject(refined, memory)

    return {
        "refined_question": refined,
        "synonym_hint": synonym_hint,
        "error_history": [],
        "retry_count": 0,
        "result_anomalies": [],
        "validation_errors": [],
    }