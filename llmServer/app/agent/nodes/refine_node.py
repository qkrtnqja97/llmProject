# llmServer/app/agent/nodes/refine_node.py

from llmServer.app.agent.graph import AgentState


def entity_linking_node(
    state: AgentState,
    entity_service,
    rag_service,
    memory_service,
):

    question = state["question"]

    # 1. 오타 보정
    refined = entity_service.fuzzy_correct(question)

    # 2. part_number 보정
    refined = rag_service.correct_part_number(refined)

    # 3. 동의어 힌트
    synonym_hint = rag_service.retrieve_synonyms(question)

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