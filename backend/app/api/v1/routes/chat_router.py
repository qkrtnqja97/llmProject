from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.api.deps import get_chat_controller, get_current_user
from app.api.v1.controllers.chat_controller import ChatController

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    # current_user: dict = Depends(get_current_user),
    controller: ChatController = Depends(get_chat_controller),
):
#    1. 스트리밍으로 결과를 받고 싶은 경우 (주석 해제 및 이름 확인)
    return StreamingResponse(
        controller.chat_stream_generator(request.prompt), 
        media_type="text/event-stream"
    )

    # 2. 일반 응답을 받고 싶은 경우 (컨트롤러에 해당 메서드가 있는지 확인 필요)
    # 만약 이름이 chat_stream_generator 뿐이라면 그걸 호출해야 합니다.
    # return await controller.chat_stream_generator(request.prompt)
