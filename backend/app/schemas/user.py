from pydantic import BaseModel, Field
from typing import List, Optional, Any

class MenuItem(BaseModel):
    id: str
    label: str
    iconName: Optional[str] = None  # 필수에서 옵션으로 변경 (안정성)
    isVisible: bool = True
    parentId: Optional[str] = None
    isGroup: bool = False
    path: Optional[str] = None 
    icon: Optional[str] = None
    # 📍 핵심: 프론트에서 재귀적으로 들어오는 children 배열을 허용해야 합니다.
    children: List["MenuItem"] = [] 

class UserSettingsSchema(BaseModel):
    theme: str = "dark"
    startPage: str = Field(..., alias="startPage") # 프론트의 camelCase 대응
    sidebarMenus: List[MenuItem]

    class Config:
        # 📍 프론트에서 보내는 JSON 필드명(startPage)을 그대로 인식하게 합니다.
        populate_by_name = True
        from_attributes = True

class UserSettingsResponse(UserSettingsSchema):
    emp_id: str
    name: Optional[str] = "사용자"
    role: str = "user"
    team: str = "general"

# 재귀 모델 정의를 위해 선언
MenuItem.model_rebuild()