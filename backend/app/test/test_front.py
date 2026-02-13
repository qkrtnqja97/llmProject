# backend/app/test/test_front.py

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat() + "Z"}

@router.get("/hello")
def hello(name: str = "world"):
    return {"msg": f"hello, {name}"}
