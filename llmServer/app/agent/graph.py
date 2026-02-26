# llmServer/app/agent/graph.py

def build_graph(services):

    def refine_node(state):
        return entity_linking_node(
            state,
            entity_service=services.entity_service,
            rag_service=services.rag_service,
            memory_service=services.memory_service,
        )

    workflow = StateGraph(AgentState)

    workflow.add_node("refine", refine_node)
