# llmServer/app/agent/nodes/router_node.py

# from app.agent.graph import AgentState

from app.services.router_service import RouterService


class RouterNode:

    def __init__(
        self,
        router_service: RouterService,
    ):
        self.router_service = router_service

    async def __call__(self, state: dict):

        question = state["question"]

        intent = await self.router_service.route(question)

        return {"intent": intent}
