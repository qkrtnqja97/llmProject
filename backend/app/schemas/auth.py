# schemas/auth.py
from pydantic import BaseModel
from typing import Optional

class UserLogin(BaseModel):
    emp_id: str
    password: str

class UserCreate(UserLogin):
    name: str
    # 📍 회원가입 시 권_한과 팀을 설정할 수 있도록 추가 (기본값 설정)
    role: Optional[str] = "user"
    team: Optional[str] = "general"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # 📍 로그인 직후 프론트엔드에서 즉시 권한을 파악할 수 있도록 추가
    role: str
    team: str
    name: str