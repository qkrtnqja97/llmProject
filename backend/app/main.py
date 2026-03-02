# backend/app/main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from app.core.lifespan import lifespan
from app.api.v1.routes.router import router as v1_router

# 1. 앱 초기화
app = FastAPI(lifespan=lifespan)

# 2. CORS 설정 (반드시 라우터 등록 전!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 곳에서 접속 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 기존 분리된 라우터 등록 (/v1/auth/login 등이 여기 포함됨)
app.include_router(v1_router, prefix="/v1")

# 4. 추가하신 테스트용 검색 엔드포인트 (선택 사항)
class Prompt(BaseModel):
    prompt: str

@app.post("/v1/search") # 중복 방지를 위해 경로를 /search로 명시
async def search(req: Prompt):
    print("프론트에서 받은 값:", req.prompt)
    return {"response": f"'{req.prompt}' 에 대한 더미 응답입니다."}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation Error: {exc.errors()}") # 터미널에 에러 상세 출력
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# 5. 실행 설정
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",
        port=8000,
        reload=True
    )