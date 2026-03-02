from fastapi import HTTPException, status
from app.services.auth_service import AuthService
from app.schemas.auth import UserLogin, Token, UserCreate

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def login(self, payload: UserLogin) -> Token:
        user = await self.auth_service.authenticate_user(payload.emp_id, payload.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사원번호 또는 비밀번호가 일치하지 않습니다."
            )
        
        # 📍 수정: 토큰 Payload에 role과 team을 심어야 함 (중요)
        token_data = {
            "sub": user['emp_id'],
            "role": user.get('role', 'user'),
            "team": user.get('team', 'general'),
            "name": user.get('name', '')
        }
        token = self.auth_service.create_access_token(data=token_data)

        return Token(
            access_token=token, 
            token_type="bearer",
            role=user.get('role', 'user'),
            team=user.get('team', 'general'),
            name=user.get('name', '')
        )

    async def register(self, payload: UserCreate):
        # 📍 수정: payload에서 role과 team을 추출하여 전달
        success = await self.auth_service.register_user(
            emp_id=payload.emp_id, 
            password=payload.password, 
            name=payload.name,
            role=payload.role or 'user',
            team=payload.team or 'general'
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 사원번호입니다."
            )
        return {"message": "회원가입 성공"}