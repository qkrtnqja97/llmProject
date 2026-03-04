from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, SessionClearRequest
from app.api.deps import get_chat_controller, get_current_user
from app.api.v1.controllers.chat_controller import ChatController

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    controller: ChatController = Depends(get_chat_controller),
):
    # 1. user_id 추출 (current_user 구조에 따라 id 또는 emp_id)
    user_id = str(current_user.get("id") or current_user.get("emp_id") or "guest")
    
    # 2. session_id 설정
    session_id = getattr(request, "session_id", "default_session")

    # 3. 컨트롤러 호출 (정의된 user_id, session_id, prompt 모두 전달)
    result = await controller.chat(
        user_id=user_id,
        session_id=session_id, 
        prompt=request.prompt
    )
    
    # 컨트롤러가 이미 response 딕셔너리를 리턴하므로 그대로 반환하거나 감싸서 반환
    return result


@router.post("/session/clear", tags=["Session"])
async def clear_session(
    request: SessionClearRequest,
    current_user: dict = Depends(get_current_user),
    controller: ChatController = Depends(get_chat_controller),
):
    """
    앱 종료 시 세션 대화 캐시를 초기화한다.
    DB 로그(conversations 테이블)는 삭제하지 않는다.
    """
    await controller.clear_session(request.session_id)
    return {"status": "ok"}