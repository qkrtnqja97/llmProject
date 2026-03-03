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
    # return await StreamingResponse(
    #     controller.chat_stream_generator(request.prompt), 
    #     media_type="text/event-stream"
    # )

    return await controller.chat(request.prompt)