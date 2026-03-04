"""
하이브리드 번역기: deep-translator(무료) + Ollama(로컬 LLM 보정)
FastAPI + Swagger(자동)
기능: 복사, 번역비교, 다크모드, 히스토리, 배치, 파일, 용어집, 다국어
"""
import os
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pydantic import BaseModel, Field
from deep_translator import GoogleTranslator
from docx import Document as DocxDocument

app = FastAPI(
    title="하이브리드 번역기 API",
    description="무료 번역 + Ollama LLM 보정 API",
    version="2.0",
)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

LANGUAGES = {
    "ko": "한국어",
    "en": "영어",
    "ja": "일본어",
    "zh-CN": "중국어(간체)",
    "zh-TW": "중국어(번체)",
    "es": "스페인어",
    "fr": "프랑스어",
    "de": "독일어",
    "ru": "러시아어",
}


class TranslateRequest(BaseModel):
    text: str = Field(..., description="번역할 텍스트")
    source: str = Field(default="ko", description="원문 언어 코드")
    target: str = Field(default="en", description="대상 언어 코드")
    use_llm: bool = Field(default=True, description="Ollama LLM 보정")
    glossary: Optional[dict[str, str]] = Field(default=None, description="용어집 {원문: 번역}")


class BatchTranslateRequest(BaseModel):
    texts: list[str] = Field(..., description="번역할 텍스트 목록")
    source: str = Field(default="ko")
    target: str = Field(default="en")
    use_llm: bool = Field(default=True)
    glossary: Optional[dict[str, str]] = Field(default=None)


class MultiTranslateRequest(BaseModel):
    text: str = Field(..., description="번역할 텍스트")
    source: str = Field(default="ko")
    targets: list[str] = Field(..., description="대상 언어 코드 목록")
    use_llm: bool = Field(default=True)
    glossary: Optional[dict[str, str]] = Field(default=None)


class EmailTranslateRequest(BaseModel):
    """바이어 메일 번역"""
    from_addr: Optional[str] = Field(default=None, description="발신자")
    subject: Optional[str] = Field(default=None, description="제목")
    body: str = Field(..., description="본문")
    source: str = Field(default="en")
    target: str = Field(default="ko")
    use_llm: bool = Field(default=True)


class TranslateResponse(BaseModel):
    translation: str
    rough: str
    refined: bool


def translate_rough(text: str, source: str, target: str) -> str:
    translator = GoogleTranslator(source=source, target=target)
    return translator.translate(text)


def refine_with_ollama(
    original: str,
    rough: str,
    source: str,
    target: str,
    glossary: Optional[dict[str, str]] = None,
) -> str | None:
    source_name = LANGUAGES.get(source, source)
    target_name = LANGUAGES.get(target, target)
    glossary_text = ""
    if glossary:
        glossary_text = "\n다음 용어는 반드시 아래처럼 번역해 주세요:\n" + "\n".join(
            f"- {k} → {v}" for k, v in glossary.items()
        ) + "\n\n"
    prompt = f"""{glossary_text}다음은 {source_name}에서 {target_name}으로의 기계 번역 결과입니다.
의미는 그대로 유지하면서 더 자연스럽고 문맥에 맞게 다듬어 주세요.
원문과 기계 번역을 참고해서 개선된 번역만 출력해 주세요. 다른 설명은 하지 마세요.

원문 ({source_name}): {original}
기계 번역 ({target_name}): {rough}

개선된 번역:"""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.RequestException:
        return None


def do_translate(
    text: str,
    source: str,
    target: str,
    use_llm: bool,
    glossary: Optional[dict[str, str]] = None,
) -> tuple[str, str, bool]:
    rough = translate_rough(text, source, target)
    if use_llm:
        refined = refine_with_ollama(text, rough, source, target, glossary)
        result = refined if refined else rough
        was_refined = bool(refined)
    else:
        result = rough
        was_refined = False
    return result, rough, was_refined


def extract_text_from_file(content: bytes, filename: str) -> str:
    """파일에서 텍스트 추출"""
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        return content.decode("utf-8", errors="replace")
    if ext in (".docx", ".doc"):
        from io import BytesIO

        doc = DocxDocument(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    raise HTTPException(status_code=400, detail=f"지원하지 않는 형식: {ext}. txt, docx만 지원합니다.")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "languages": LANGUAGES})


@app.post("/api/translate", response_model=TranslateResponse)
async def translate(body: TranslateRequest):
    """단일 번역"""
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="번역할 텍스트를 입력해 주세요.")
    try:
        result, rough, was_refined = do_translate(
            text, body.source, body.target, body.use_llm, body.glossary
        )
        return TranslateResponse(translation=result, rough=rough, refined=was_refined)
    except Exception as e:
        err_msg = str(e).lower()
        if "connection" in err_msg or "timeout" in err_msg:
            raise HTTPException(status_code=500, detail="번역 서비스에 연결할 수 없습니다.")
        if "invalid" in err_msg or "language" in err_msg:
            raise HTTPException(status_code=400, detail="지원하지 않는 언어 쌍입니다.")
        raise HTTPException(status_code=500, detail=f"번역 실패: {str(e)}")


@app.post("/api/translate/batch")
async def translate_batch(body: BatchTranslateRequest):
    """배치 번역 - 여러 문장 한 번에"""
    if not body.texts:
        raise HTTPException(status_code=400, detail="번역할 텍스트가 없습니다.")
    results = []
    for t in body.texts:
        text = (t or "").strip()
        if not text:
            results.append({"original": t, "translation": "", "rough": "", "refined": False})
            continue
        try:
            result, rough, was_refined = do_translate(
                text, body.source, body.target, body.use_llm, body.glossary
            )
            results.append({"original": text, "translation": result, "rough": rough, "refined": was_refined})
        except Exception:
            results.append({"original": text, "translation": "[번역 실패]", "rough": "", "refined": False})
    return {"results": results}


@app.post("/api/translate/multi")
async def translate_multi(body: MultiTranslateRequest):
    """다국어 동시 번역"""
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="번역할 텍스트를 입력해 주세요.")
    if not body.targets:
        raise HTTPException(status_code=400, detail="대상 언어를 선택해 주세요.")
    outputs = {}
    for target in body.targets:
        try:
            result, rough, was_refined = do_translate(
                text, body.source, target, body.use_llm, body.glossary
            )
            outputs[target] = {"translation": result, "rough": rough, "refined": was_refined}
        except Exception:
            outputs[target] = {"translation": "[번역 실패]", "rough": "", "refined": False}
    return {"results": outputs}


@app.post("/api/translate/file")
async def translate_file(
    file: UploadFile = File(...),
    source: str = Form("ko"),
    target: str = Form("en"),
    use_llm: str = Form("true"),
):
    """파일 업로드 번역 (txt, docx)"""
    content = await file.read()
    try:
        full_text = extract_text_from_file(content, file.filename or "")
    except HTTPException:
        raise
    if not full_text.strip():
        raise HTTPException(status_code=400, detail="파일 내용이 비어 있습니다.")
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
    results = []
    for p in paragraphs:
        try:
            result, rough, was_refined = do_translate(p, source, target, use_llm.lower() == "true", None)
            results.append({"original": p, "translation": result, "rough": rough, "refined": was_refined})
        except Exception:
            results.append({"original": p, "translation": "[번역 실패]", "rough": "", "refined": False})
    return {"filename": file.filename, "results": results}


@app.post("/api/translate/email")
async def translate_email(body: EmailTranslateRequest):
    """바이어 메일 번역 - 발신자, 제목, 본문"""
    body_text = (body.body or "").strip()
    if not body_text:
        raise HTTPException(status_code=400, detail="본문을 입력해 주세요.")
    try:
        body_result, _, _ = do_translate(
            body_text, body.source, body.target, body.use_llm, None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"본문 번역 실패: {str(e)}")

    subject_result = ""
    if (body.subject or "").strip():
        try:
            subject_result, _, _ = do_translate(
                body.subject.strip(), body.source, body.target, body.use_llm, None
            )
        except Exception:
            subject_result = body.subject

    return {
        "from": body.from_addr or "",
        "subject_original": body.subject or "",
        "subject_translated": subject_result,
        "body_original": body_text,
        "body_translated": body_result,
    }


@app.get("/api/languages")
async def languages():
    return LANGUAGES


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
