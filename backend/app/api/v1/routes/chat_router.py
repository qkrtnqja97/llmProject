from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest
from app.api.deps import get_chat_controller
from app.api.v1.controllers.chat_controller import ChatController

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    controller: ChatController = Depends(get_chat_controller),
):
    return await controller.chat(request.prompt)