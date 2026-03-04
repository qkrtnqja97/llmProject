from fastapi import APIRouter, UploadFile, File, Form
from app.api.v1.controllers.translate_controller import TranslateController
from app.schemas.translate import (
    TranslateRequest, TranslateResponse, BatchTranslateRequest, MultiTranslateRequest, EmailTranslateRequest
)
from app.services.translate_service import LANGUAGES

router = APIRouter()

@router.get("/languages")
async def get_languages():
    return LANGUAGES

@router.post("/", response_model=TranslateResponse)
async def translate_single(body: TranslateRequest):
    return await TranslateController.translate_single(body)

@router.post("/batch")
async def translate_batch(body: BatchTranslateRequest):
    return await TranslateController.translate_batch(body)

@router.post("/multi")
async def translate_multi(body: MultiTranslateRequest):
    return await TranslateController.translate_multi(body)

@router.post("/file")
async def translate_file(
    file: UploadFile = File(...),
    source: str = Form("ko"),
    target: str = Form("en"),
    use_llm: bool = Form(True)
):
    return await TranslateController.translate_file(file, source, target, use_llm)

@router.post("/email")
async def translate_email(body: EmailTranslateRequest):
    return await TranslateController.translate_email(body)