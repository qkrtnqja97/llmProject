import json
from typing import List, Dict, Any
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserSettingsSchema

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _get_default_menus(self, role: str, team: str) -> List[Dict[str, Any]]:
        """
        프론트엔드 Sidebar.tsx의 baseMenus 로직을 백엔드로 완벽 이식
        """
        # 1. 공통 기본 메뉴
        menus = [
            {"id": "ai-search", "label": "AI 업무검색", "path": "/ai-search", "isVisible": True, "iconName": "Search", "parentId": None},
            {"id": "dashboard", "label": "대시보드", "path": "/dashboard", "isVisible": True, "iconName": "LayoutDashboard", "parentId": None},
            
            {"id": "group-work", "label": "업무 관리", "isVisible": True, "iconName": "Briefcase", "parentId": None, "isGroup": True},
            {"id": "work-create", "label": "업무 작성", "path": "/work/create", "isVisible": True, "iconName": "PenLine", "parentId": "group-work"},
            {"id": "work-log", "label": "일지 작성", "path": "/work/log", "isVisible": True, "iconName": "FileText", "parentId": "group-work"},
            {"id": "work-memo", "label": "회의록", "path": "/work/memo", "isVisible": True, "iconName": "StickyNote", "parentId": "group-work"},
        ]

        # 2. 인사/행정 (admin 또는 hr 팀)
        if role == "admin" or team == "hr":
            menus.extend([
                {"id": "group-hr", "label": "인사/행정", "isVisible": True, "iconName": "Users2", "parentId": None, "isGroup": True},
                {"id": "hr-emp", "label": "사원 관리", "path": "/hr/employees", "isVisible": True, "iconName": "UserCog", "parentId": "group-hr"},
                {"id": "hr-att", "label": "근태 기록", "path": "/hr/attendance", "isVisible": True, "iconName": "CalendarCheck", "parentId": "group-hr"},
            ])

        # 3. 회계/재무 (admin 또는 finance 팀)
        if role == "admin" or team == "finance":
            menus.extend([
                {"id": "group-finance", "label": "회계/재무", "isVisible": True, "iconName": "Landmark", "parentId": None, "isGroup": True},
                {"id": "finance-voucher", "label": "전표 관리", "path": "/finance/voucher", "isVisible": True, "iconName": "ReceiptText", "parentId": "group-finance"},
                {"id": "finance-settlement", "label": "결산 보고", "path": "/finance/settlement", "isVisible": True, "iconName": "BarChart3", "parentId": "group-finance"},
            ])

        # 4. 영업/판매 (admin 또는 sales 팀)
        if role == "admin" or team == "sales":
            menus.extend([
                {"id": "group-sales", "label": "영업/판매", "isVisible": True, "iconName": "BadgeDollarSign", "parentId": None, "isGroup": True},
                {"id": "sales-quote", "label": "견적 관리", "path": "/sales/quote", "isVisible": True, "iconName": "Quote", "parentId": "group-sales"},
                {"id": "sales-order", "label": "수주 관리", "path": "/sales/order-so", "isVisible": True, "iconName": "FileSpreadsheet", "parentId": "group-sales"},
            ])

        # 5. 운영 관리/ERP (admin 또는 purchase, logistics, product 팀)
        if role == "admin" or team in ["purchase", "logistics", "product"]:
            menus.extend([
                {"id": "group-manage", "label": "운영 관리", "isVisible": True, "iconName": "Settings2", "parentId": None, "isGroup": True},
                {"id": "manage-inventory", "label": "재고 관리", "path": "/manage/inventory", "isVisible": True, "iconName": "Box", "parentId": "group-manage"},
                {"id": "manage-order", "label": "발주 관리", "path": "/manage/order", "isVisible": True, "iconName": "ShoppingCart", "parentId": "group-manage"},
                {"id": "manage-product", "label": "제품 관리", "path": "/manage/product", "isVisible": True, "iconName": "Package", "parentId": "group-manage"},
            ])

        # 6. 하단 공통 메뉴
        menus.extend([
            {"id": "contact", "label": "연락처", "path": "/contact", "isVisible": True, "iconName": "Contact2", "parentId": None},
            {"id": "resources", "label": "자료실", "path": "/resources", "isVisible": True, "iconName": "FolderOpen", "parentId": None},
            {"id": "history", "label": "검색 기록", "path": "/history", "isVisible": True, "iconName": "History", "parentId": None}
        ])
        
        return menus

    async def get_settings(self, emp_id: str):
        user = await self.user_repo.get_user_by_emp_id(emp_id)
        settings = await self.user_repo.get_user_settings(emp_id)
        
        user_role = user['role'] if user else 'user'
        user_team = user['team'] if user else 'general'
        user_name = user['name'] if user else '사용자'

        default_menus = self._get_default_menus(user_role, user_team)

        if not settings:
            return {
                "emp_id": emp_id, "name": user_name, "theme": "dark",
                "startPage": "/ai-search", "sidebarMenus": default_menus,
                "role": user_role, "team": user_team
            }
        
        settings_dict = dict(settings)
        sidebar_data = settings_dict.get("menu_config") or settings_dict.get("sidebarMenus")
        
        saved_menus = []
        if isinstance(sidebar_data, str):
            try: saved_menus = json.loads(sidebar_data)
            except: saved_menus = default_menus
        elif isinstance(sidebar_data, list):
            saved_menus = sidebar_data
        else:
            saved_menus = default_menus

        # 📍 병합: 프론트에서 추가한 신규 그룹/메뉴가 DB에 없으면 자동으로 추가
        saved_ids = {m['id'] for m in saved_menus}
        for d_menu in default_menus:
            if d_menu['id'] not in saved_ids:
                saved_menus.append(d_menu)

        return {
            "emp_id": emp_id,
            "name": user_name,
            "theme": settings_dict.get("theme", "dark"),
            "startPage": settings_dict.get("start_page") or "/ai-search",
            "sidebarMenus": saved_menus,
            "role": user_role,
            "team": user_team
        }

    async def save_settings(self, emp_id: str, payload: UserSettingsSchema):
        processed_menus = []
        for item in payload.sidebarMenus:
            m_dict = item.model_dump() if hasattr(item, 'model_dump') else item.dict()
            # 프론트와 DB 필드명(iconName) 동기화
            if not m_dict.get('iconName'):
                m_dict['iconName'] = m_dict.get('icon', 'Grid')
            m_dict['icon'] = m_dict['iconName']
            processed_menus.append(m_dict)

        await self.user_repo.upsert_user_settings(
            emp_id=emp_id, 
            theme=payload.theme, 
            start_page=payload.startPage, 
            menu_config=json.dumps(processed_menus, ensure_ascii=False)
        )