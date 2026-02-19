# llmServer/api/generate.py
# LLM 서버의 텍스트 생성 API 엔드포인트 정의

from fastapi import APIRouter, Request
from llm_server.schemas import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, request: Request):
    model = request.app.state.model

    output = model.generate(req.prompt)

    return GenerateResponse(text=output)
