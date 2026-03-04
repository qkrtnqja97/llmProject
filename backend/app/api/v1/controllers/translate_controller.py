from fastapi import HTTPException, UploadFile
from app.services.translate_service import TranslateService
from app.schemas.translate import (
    TranslateRequest, BatchTranslateRequest, MultiTranslateRequest, EmailTranslateRequest
)

class TranslateController:
    @staticmethod
    async def translate_single(body: TranslateRequest):
        try:
            res, rough, refined = TranslateService.do_translate(
                body.text, body.source, body.target, body.use_llm, body.glossary
            )
            return {"translation": res, "rough": rough, "refined": refined}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def translate_batch(body: BatchTranslateRequest):
        results = []
        for t in body.texts:
            res, rough, refined = TranslateService.do_translate(t, body.source, body.target, body.use_llm, body.glossary)
            results.append({"original": t, "translation": res, "rough": rough, "refined": refined})
        return {"results": results}

    @staticmethod
    async def translate_multi(body: MultiTranslateRequest):
        results = {}
        for target in body.targets:
            res, rough, refined = TranslateService.do_translate(body.text, body.source, target, body.use_llm, body.glossary)
            results[target] = {"translation": res, "rough": rough, "refined": refined}
        return {"results": results}

    @staticmethod
    async def translate_file(file: UploadFile, source: str, target: str, use_llm: bool):
        try:
            content = await file.read()
            full_text = TranslateService.extract_text(content, file.filename)
            paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
            results = []
            for p in paragraphs:
                res, rough, refined = TranslateService.do_translate(p, source, target, use_llm)
                results.append({"original": p, "translation": res, "rough": rough, "refined": refined})
            return {"filename": file.filename, "results": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def translate_email(body: EmailTranslateRequest):
        body_res, _, _ = TranslateService.do_translate(body.body, body.source, body.target, body.use_llm)
        subject_res = body.subject
        if body.subject:
            subject_res, _, _ = TranslateService.do_translate(body.subject, body.source, body.target, body.use_llm)
        return {
            "from": body.from_addr,
            "subject_original": body.subject,
            "subject_translated": subject_res,
            "body_original": body.body,
            "body_translated": body_res
        }