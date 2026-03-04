from fastapi import APIRouter, Depends
from pydantic import BaseModel
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


class SessionClearRequest(BaseModel):
    session_id: str


@router.post("/session/clear", tags=["Session"])
async def clear_session_cache(
    request: SessionClearRequest,
    container = Depends(get_container),
):
    """
    앱 종료 시 세션 대화 캐시를 초기화한다.
    DB 로그(conversations 테이블)는 삭제하지 않는다.
    """
    await container.memory_service.clear_context_cache(request.session_id)
    return {"status": "ok"}