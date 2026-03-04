import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

# 기존 lifespan 및 router 로드
from app.core.lifespan import lifespan
from app.api.v1.routes.router import router as v1_router
# 신규 번역 라우터 (router.py에서 include_router 해도 됩니다)
from app.api.v1.routes.translate_router import router as translate_router

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://frames-criteria-livestock-acknowledge.trycloudflare.com", # ✅ 프론트엔드 터널 주소 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(v1_router, prefix="/v1")
app.include_router(translate_router, prefix="/v1/translate", tags=["Translation"])

# 테스트용 검색 엔드포인트
class Prompt(BaseModel):
    prompt: str

@app.post("/v1/search")
async def search(req: Prompt):
    return {"response": f"'{req.prompt}' 에 대한 응답입니다."}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
