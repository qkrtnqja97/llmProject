from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.api.deps import get_chat_controller, get_current_user
from app.api.v1.controllers.chat_controller import ChatController

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    controller: ChatController = Depends(get_chat_controller),
):
    # ❌ 기존 스트리밍 방식 (주석 처리)
    # return StreamingResponse(
    #     controller.chat_stream_generator(request.prompt), 
    #     media_type="text/event-stream"
    # )

    # ✅ 일반 JSON 응답 방식 (수정)
    # 컨트롤러에서 스트리밍이 아닌 최종 답변 문자열을 반환하는 메서드를 호출해야 합니다.
    # 만약 chat_stream_generator만 있다면, 내부 로직을 모아서 리턴하는 메서드를 추가하거나 아래처럼 호출하세요.
    
    result = await controller.chat(request.prompt) # 컨트롤러에 일반 chat 메서드가 있다고 가정
    return {"answer": result}