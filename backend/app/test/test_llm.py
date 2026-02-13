# backend/app/test/test_llm.py

from fastapi import APIRouter
from app.test.test_llm_client import llm_health_check

router = APIRouter()

@router.get("/health")
def llm_health():
    return llm_health_check()
