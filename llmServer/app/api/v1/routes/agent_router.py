from fastapi import APIRouter, Depends
from app.schemas.agent_schema import AgentRequest, AgentResponse
from app.dependency import get_container
from app.agent.agent_graph import build_graph
from app.application.agent_controller import AgentController


router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/query", response_model=AgentResponse)
async def query_agent(
    request: AgentRequest,
    container = Depends(get_container)
):

    graph = build_graph(container)
    controller = AgentController(graph)

    result = await controller.run(
        user_id=request.user_id,
        session_id=request.session_id,
        question=request.question,
    )

    return result