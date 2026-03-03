# backend/app/api/deps.py
import httpx
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# 1. Core & Config
from app.core.config import settings

# 2. Clients (AI 관련)
from app.clients.ai.llm_client import LLMClient

# 3. Repositories (각 도메인별 리포지토리)
from app.repositories.user_repository import UserRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.work_repository import WorkRepository
from app.repositories.inventory_repository import InventoryRepository

# 4. Services (비즈니스 로직)
from app.services.chat_service import ChatService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.dashboard_service import DashboardService
from app.services.work_service import WorkService
from app.services.inventory_service import InventoryService

# 5. Controllers (API 흐름 제어)
from app.api.v1.controllers.chat_controller import ChatController
from app.api.v1.controllers.auth_controller import AuthController
from app.api.v1.controllers.user_controller import UserController
from app.api.v1.controllers.dashboard_controller import DashboardController
from app.api.v1.controllers.work_controller import WorkController
from app.api.v1.controllers.inventory_controller import InventoryController

# --- 인증 관련 설정 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

# --- Dependency Injection Functions ---

def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client
def get_llm_client(http_client: httpx.AsyncClient = Depends(get_http_client)) -> LLMClient:
    return LLMClient(http_client)
def get_chat_service(llm_client: LLMClient = Depends(get_llm_client)) -> ChatService:
    return ChatService(llm_client)

# DB Repository 주입
def get_user_repository(request: Request) -> UserRepository:
    return UserRepository(request.app.state.db_pool)
def get_dashboard_repository(request: Request) -> DashboardRepository:
    return DashboardRepository(request.app.state.db_pool)
def get_work_repository(request: Request) -> WorkRepository:
    return WorkRepository(request.app.state.db_pool)
def get_inventory_repository(request: Request) -> InventoryRepository: # 📍 추가
    return InventoryRepository(request.app.state.db_pool)

# Service 주입
def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)
def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)
def get_chat_service(llm_client: LLMClient = Depends(get_llm_client),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository)) -> ChatService:
    return ChatService(llm_client, inventory_repo)
def get_dashboard_service(dashboard_repo: DashboardRepository = Depends(get_dashboard_repository)) -> DashboardService:
    return DashboardService(dashboard_repo)
def get_work_service(work_repo: WorkRepository = Depends(get_work_repository)) -> WorkService:
    return WorkService(work_repo)
def get_inventory_service(inventory_repo: InventoryRepository = Depends(get_inventory_repository)) -> InventoryService: # 📍 추가
    return InventoryService(inventory_repo)

# Controller 주입
def get_chat_controller(chat_service: ChatService = Depends(get_chat_service)) -> ChatController:
    return ChatController(chat_service)
def get_auth_controller(auth_service: AuthService = Depends(get_auth_service)) -> AuthController:
    return AuthController(auth_service)
def get_user_controller(user_service: UserService = Depends(get_user_service)) -> UserController:
    return UserController(user_service)
def get_dashboard_controller(dashboard_service: DashboardService = Depends(get_dashboard_service)) -> DashboardController:
    return DashboardController(dashboard_service)
def get_work_controller(work_service: WorkService = Depends(get_work_service)) -> WorkController:
    return WorkController(work_service)
def get_inventory_controller(inventory_service: InventoryService = Depends(get_inventory_service)) -> InventoryController: # 📍 추가
    return InventoryController(inventory_service)

# --- get_current_user (인증 로직) ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        emp_id: str = payload.get("sub")
        if emp_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await user_repo.get_user_by_emp_id(emp_id)
    if user is None:
        raise credentials_exception
    return user
