import bcrypt
import json
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.repositories.user_repository import UserRepository
from app.core.config import settings

# 📍 passlib (pwd_context) 대신 bcrypt를 직접 사용하여 에러를 원천 차단합니다.

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, emp_id: str, password: str):
        user = await self.user_repo.get_user_by_emp_id(emp_id)
        if not user:
            return None

        # 📍 비밀번호 검증 (bcrypt 직접 사용)
        try:
            stored_password = user['password']
            # DB의 해시가 문자열(str)이면 bytes로 변환
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            # 입력받은 비밀번호를 bytes로 변환 후 검증
            is_valid = bcrypt.checkpw(
                password.encode('utf-8'), 
                stored_password
            )
            
            if is_valid:
                return user
        except Exception as e:
            print(f"❌ 비밀번호 검증 중 오류 발생: {e}")
            
        return None

    async def register_user(self, emp_id, password, name, role='user', team='general'):
        """유저 등록 시 권한(role)과 팀(team)에 따른 메뉴 차등 부여"""
        existing = await self.user_repo.get_user_by_emp_id(emp_id)
        if existing: 
            return False
        
        # 📍 비밀번호 해싱 (bcrypt 직접 사용)
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_str = hashed_bytes.decode('utf-8') # DB 저장을 위해 문자열로 변환

        await self.user_repo.create_user(emp_id, hashed_str, name, role, team)
        
        # ✅ 사이드바 트리 구조 (기존 로직 유지)
        default_menus_list = [
            {"id": "ai-search", "label": "AI 업무검색", "path": "/ai-search", "isVisible": True, "icon": "Search", "parentId": None},
            {"id": "dashboard", "label": "대시보드", "path": "/dashboard", "isVisible": True, "icon": "LayoutDashboard", "parentId": None},
            {"id": "group-work", "label": "업무 관리", "isVisible": True, "icon": "Briefcase", "parentId": None, "isGroup": True},
            {"id": "work-create", "label": "업무 작성", "path": "/work/create", "isVisible": True, "icon": "PenLine", "parentId": "group-work"},
            {"id": "work-log", "label": "일지 작성", "path": "/work/log", "isVisible": True, "icon": "FileText", "parentId": "group-work"},
            {"id": "work-memo", "label": "메모장", "path": "/work/memo", "isVisible": True, "icon": "StickyNote", "parentId": "group-work"},
        ]

        if role == 'admin' or team == 'product':
            default_menus_list.extend([
                {"id": "group-manage", "label": "운영 관리", "isVisible": True, "icon": "Settings2", "parentId": None, "isGroup": True},
                {"id": "manage-inventory", "label": "재고 관리", "path": "/manage/inventory", "isVisible": True, "icon": "Box", "parentId": "group-manage"},
                {"id": "manage-order", "label": "발주 관리", "path": "/manage/order", "isVisible": True, "icon": "ShoppingCart", "parentId": "group-manage"},
                {"id": "manage-product", "label": "제품 관리", "path": "/manage/product", "isVisible": True, "icon": "Package", "parentId": "group-manage"},
            ])

        default_menus_list.extend([
            {"id": "contact", "label": "연락처", "path": "/contact", "isVisible": True, "icon": "Users", "parentId": None},
            {"id": "resources", "label": "자료실", "path": "/resources", "isVisible": True, "icon": "FolderOpen", "parentId": None},
            {"id": "history", "label": "검색 기록", "path": "/history", "isVisible": True, "icon": "History", "parentId": None}
        ])
    
        default_menus_json = json.dumps(default_menus_list, ensure_ascii=False)
        await self.user_repo.upsert_user_settings(emp_id, "dark", "/ai-search", default_menus_json)
        return True

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)