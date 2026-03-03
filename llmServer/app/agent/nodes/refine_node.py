# llmServer/app/agent/nodes/refine_node.py

from typing import Dict
from app.container import ServiceContainer

class RefineNode:
    """
    EntityResolverService → refined_question 보정 + synonym_hint
    """

    def __init__(self, container: ServiceContainer):
        self.entity_service = container.entity_service

    async def __call__(self, state: Dict) -> Dict:
      result = await self.entity_service.resolve(state["refined_question"])

      new_state = state.copy()
      new_state.update(result)
      return new_state