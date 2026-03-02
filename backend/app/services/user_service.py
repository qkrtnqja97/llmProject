import json
import logging
from typing import List, Dict, Any
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserSettingsSchema

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _get_default_menus(self, role: str, team: str) -> List[Dict[str, Any]]:
        """
        시스템 권한 및 팀별 표준 메뉴 구성 (아이콘 및 경로의 기준점)
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

        # 2. 인사/행정
        if role == "admin" or team == "hr":
            menus.extend([
                {"id": "group-hr", "label": "인사/행정", "isVisible": True, "iconName": "Users2", "parentId": None, "isGroup": True},
                {"id": "hr-emp", "label": "사원 관리", "path": "/hr/employees", "isVisible": True, "iconName": "UserCog", "parentId": "group-hr"},
                {"id": "hr-att", "label": "근태 기록", "path": "/hr/attendance", "isVisible": True, "iconName": "CalendarCheck", "parentId": "group-hr"},
            ])

        # 3. 회계/재무
        if role == "admin" or team == "finance":
            menus.extend([
                {"id": "group-finance", "label": "회계/재무", "isVisible": True, "iconName": "Landmark", "parentId": None, "isGroup": True},
                {"id": "finance-voucher", "label": "전표 관리", "path": "/finance/voucher", "isVisible": True, "iconName": "ReceiptText", "parentId": "group-finance"},
                {"id": "finance-settlement", "label": "결산 보고", "path": "/finance/settlement", "isVisible": True, "iconName": "BarChart3", "parentId": "group-finance"},
            ])

        # 4. 영업/판매
        if role == "admin" or team == "sales":
            menus.extend([
                {"id": "group-sales", "label": "영업/판매", "isVisible": True, "iconName": "BadgeDollarSign", "parentId": None, "isGroup": True},
                {"id": "sales-quote", "label": "견적 관리", "path": "/sales/quote", "isVisible": True, "iconName": "Quote", "parentId": "group-sales"},
                {"id": "sales-order", "label": "수주 관리", "path": "/sales/order-so", "isVisible": True, "iconName": "FileSpreadsheet", "parentId": "group-sales"},
            ])

        # 5. 운영 관리 (ERP)
        if role == "admin" or team in ["purchase", "logistics", "product"]:
            menus.extend([
                {"id": "group-manage", "label": "ERP/재고", "isVisible": True, "iconName": "Box", "parentId": None, "isGroup": True},
                {"id": "manage-inventory", "label": "재고 관리", "path": "/manage/inventory", "isVisible": True, "iconName": "Box", "parentId": "group-manage"},
                {"id": "manage-order", "label": "발주 관리", "path": "/manage/order", "isVisible": True, "iconName": "ShoppingCart", "parentId": "group-manage"},
                {"id": "manage-product", "label": "제품 관리", "path": "/manage/product", "isVisible": True, "iconName": "Package", "parentId": "group-manage"},
            ])

        # 6. 하단 공통 메뉴
        menus.extend([
            {"id": "contact", "label": "연락처", "path": "/contact", "isVisible": True, "iconName": "Users", "parentId": None},
            {"id": "resources", "label": "자료실", "path": "/resources", "isVisible": True, "iconName": "FolderOpen", "parentId": None},
            {"id": "history", "label": "검색 기록", "path": "/history", "isVisible": True, "iconName": "History", "parentId": None}
        ])
        
        return menus

    async def get_settings(self, emp_id: str) -> Dict[str, Any]:
        """
        설정을 로드하고, DB 데이터와 시스템 표준(아이콘/경로)을 병합하여 반환합니다.
        """
        user = await self.user_repo.get_user_by_emp_id(emp_id)
        settings = await self.user_repo.get_user_settings(emp_id)
        
        user_role = user['role'] if user else 'user'
        user_team = user['team'] if user else 'general'
        user_name = user['name'] if user else '사용자'

        default_menus = self._get_default_menus(user_role, user_team)

        if not settings:
            return {
                "emp_id": emp_id, "name": user_name, "theme": "navy",
                "startPage": "/ai-search", "sidebarMenus": default_menus,
                "role": user_role, "team": user_team
            }
        
        settings_dict = dict(settings)
        raw_data = settings_dict.get("menu_config") or settings_dict.get("sidebarMenus")
        
        saved_menus = []
        if isinstance(raw_data, str):
            try: saved_menus = json.loads(raw_data)
            except: saved_menus = default_menus
        elif isinstance(raw_data, list):
            saved_menus = raw_data
        else:
            saved_menus = default_menus

        # 📍 [핵심: 아이콘 복구 및 병합 로직]
        # DB에 저장된 'isVisible' 설정은 유지하되, 'iconName', 'path' 등은 백엔드 정의값을 강제로 씌움
        final_menus = []
        saved_map = {m['id']: m for m in saved_menus}

        for d_menu in default_menus:
            m_id = d_menu['id']
            if m_id in saved_map:
                s_menu = saved_map[m_id]
                # 병합: 사용자 설정(isVisible) + 시스템 표준(아이콘/경로)
                merged_item = {
                    **d_menu,  # 시스템 표준 데이터(아이콘 포함)를 베이스로 함
                    "isVisible": s_menu.get("isVisible", True), # 노출 여부만 유저 설정값 반영
                    "label": s_menu.get("label") or d_menu["label"]
                }
                final_menus.append(merged_item)
            else:
                # DB에 없는 신규 메뉴 추가
                final_menus.append(d_menu)

        return {
            "emp_id": emp_id,
            "name": user_name,
            "theme": settings_dict.get("theme", "navy"),
            "startPage": settings_dict.get("start_page") or "/ai-search",
            "sidebarMenus": final_menus,
            "role": user_role,
            "team": user_team
        }

    async def save_settings(self, emp_id: str, payload: UserSettingsSchema):
        """
        사용자 설정을 안전하게 DB에 저장합니다.
        """
        processed_menus = []
        source_menus = payload.sidebarMenus if isinstance(payload.sidebarMenus, list) else []

        for item in source_menus:
            # Pydantic 모델 변환 처리
            if hasattr(item, 'model_dump'): m_dict = item.model_dump()
            elif hasattr(item, 'dict'): m_dict = item.dict()
            else: m_dict = dict(item)
            
            # 아이콘 유실 방지: iconName이 없으면 icon 필드라도 참조
            icon_to_save = m_dict.get('iconName') or m_dict.get('icon') or 'Grid'
            
            # 필요한 필드만 정제하여 저장 (DB 용량 및 구조 최적화)
            processed_menus.append({
                "id": m_dict.get('id'),
                "label": m_dict.get('label'),
                "path": m_dict.get('path'),
                "isVisible": m_dict.get('isVisible', True),
                "iconName": icon_to_save,
                "parentId": m_dict.get('parentId'),
                "isGroup": m_dict.get('isGroup', False)
            })

        await self.user_repo.upsert_user_settings(
            emp_id=emp_id, 
            theme=payload.theme, 
            start_page=payload.startPage, 
            menu_config=json.dumps(processed_menus, ensure_ascii=False)
        )