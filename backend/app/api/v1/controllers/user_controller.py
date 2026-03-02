# app/api/v1/controllers/user_controller.py

from app.services.user_service import UserService
from app.schemas.user import UserSettingsSchema


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def get_settings(self, emp_id: str):
        settings = await self.user_service.get_settings(emp_id)
        return settings

    async def update_settings(self, emp_id: str, payload: UserSettingsSchema):
        # 1. 설정 저장 수행
        await self.user_service.save_settings(emp_id, payload)
        
        # 2. [수정] router의 response_model(UserSettingsResponse) 규격에 맞춰 데이터 반환
        # 단순히 메시지만 보내지 않고, 업데이트된 모든 정보를 포함시킵니다.
        return {
            "emp_id": emp_id,
            "theme": payload.theme,
            "startPage": payload.startPage,
            "sidebarMenus": payload.sidebarMenus,
            "status": "success",
            "message": "설정이 저장되었습니다."
        }