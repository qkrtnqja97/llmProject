# app/api/v1/routes/user_router.py

from fastapi import APIRouter, Depends
from app.api.deps import get_user_controller, get_current_user
from app.api.v1.controllers.user_controller import UserController
from app.schemas.user import UserSettingsSchema, UserSettingsResponse

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/settings")
async def get_settings(
    current_user: dict = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    return await controller.get_settings(current_user["emp_id"])

@router.post("/settings", response_model=UserSettingsResponse)
async def update_settings(
    payload: UserSettingsSchema,
    current_user: dict = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    return await controller.update_settings(current_user["emp_id"], payload)