# backend/app/test/test_main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.test.test_front import router as front_router
from app.test.test_llm import router as llm_router

load_dotenv()

app = FastAPI(title="Integration Test Gateway", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# front 관련 요청
app.include_router(
    front_router,
    prefix="",
    tags=["front-test"]
)

# llm 관련 요청
app.include_router(
    llm_router,
    prefix="/llm",
    tags=["llm-test"]
)

@app.get("/")
def root():
    return {
        "app": os.getenv("APP_NAME"),
        "env": os.getenv("APP_ENV"),
    }