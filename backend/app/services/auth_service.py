from app.repositories.user_repository import UserRepository
from app.core.config import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
import json

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__ident="2b" 
)

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, emp_id: str, password: str):
        user = await self.user_repo.get_user_by_emp_id(emp_id)
        if user and pwd_context.verify(password, user['password']):
            return user
        return None

    async def register_user(self, emp_id, password, name, role='user', team='general'):
        """유저 등록 시 권한(role)과 팀(team)에 따른 메뉴 차등 부여"""
        existing = await self.user_repo.get_user_by_emp_id(emp_id)
        if existing: return False
        
        hashed = pwd_context.hash(password)
        await self.user_repo.create_user(emp_id, hashed, name, role, team)
        
        # ✅ 사이드바 트리 구조를 고려한 기본 메뉴 구성
        default_menus_list = [
            {"id": "ai-search", "label": "AI 업무검색", "path": "/ai-search", "isVisible": True, "icon": "Search", "parentId": None},
            {"id": "dashboard", "label": "대시보드", "path": "/dashboard", "isVisible": True, "icon": "LayoutDashboard", "parentId": None},
            
            # 업무 관리 그룹
            {"id": "group-work", "label": "업무 관리", "isVisible": True, "icon": "Briefcase", "parentId": None, "isGroup": True},
            {"id": "work-create", "label": "업무 작성", "path": "/work/create", "isVisible": True, "icon": "PenLine", "parentId": "group-work"},
            {"id": "work-log", "label": "일지 작성", "path": "/work/log", "isVisible": True, "icon": "FileText", "parentId": "group-work"},
            {"id": "work-memo", "label": "메모장", "path": "/work/memo", "isVisible": True, "icon": "StickyNote", "parentId": "group-work"},
        ]

        # 운영 관리 그룹
        if role == 'admin' or team == 'product':
            default_menus_list.extend([
                {"id": "group-manage", "label": "운영 관리", "isVisible": True, "icon": "Settings2", "parentId": None, "isGroup": True},
                {"id": "manage-inventory", "label": "재고 관리", "path": "/manage/inventory", "isVisible": True, "icon": "Box", "parentId": "group-manage"},
                {"id": "manage-order", "label": "발주 관리", "path": "/manage/order", "isVisible": True, "icon": "ShoppingCart", "parentId": "group-manage"},
                {"id": "manage-product", "label": "제품 관리", "path": "/manage/product", "isVisible": True, "icon": "Package", "parentId": "group-manage"},
            ])

        # 공통 메뉴 추가
        default_menus_list.extend([
            {"id": "contact", "label": "연락처", "path": "/contact", "isVisible": True, "icon": "Users", "parentId": None},
            {"id": "resources", "label": "자료실", "path": "/resources", "isVisible": True, "icon": "FolderOpen", "parentId": None},
            {"id": "history", "label": "검색 기록", "path": "/history", "isVisible": True, "icon": "History", "parentId": None}
        ])
    
        default_menus_json = json.dumps(default_menus_list, ensure_ascii=False)
        
        # upsert_user_settings가 DB의 어떤 컬럼에 저장하는지 확인 필요 (예: menu_config)
        await self.user_repo.upsert_user_settings(emp_id, "dark", "/ai-search", default_menus_json)
        return True

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)