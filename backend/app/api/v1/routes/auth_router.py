from fastapi import APIRouter, Depends
from app.api.deps import get_auth_controller
from app.api.v1.controllers.auth_controller import AuthController
from app.schemas.auth import UserLogin, Token, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin, 
    controller: AuthController = Depends(get_auth_controller)
):
    return await controller.login(payload)

@router.post("/register")
async def register(
    payload: UserCreate, # UserLogin 대신 UserCreate 사용
    controller: AuthController = Depends(get_auth_controller)
):
    # 이제 payload.name 에 접근 가능합니다.
    return await controller.register(payload)