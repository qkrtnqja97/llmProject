from fastapi import APIRouter, Depends
from app.schemas.chat import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService
from app.deps import get_llm_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: LLMService = Depends(get_llm_service),
):

    result = await service.generate(
        prompt=request.prompt,
    )

    return GenerateResponse(response=result)