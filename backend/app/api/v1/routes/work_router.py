# app/api/v1/routes/work_router.py
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_work_controller, get_current_user
from app.api.v1.controllers.work_controller import WorkController
from app.schemas.work import TaskCreate, TaskResponse, TaskListResponse

router = APIRouter(prefix="/work", tags=["work"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    current_user: dict = Depends(get_current_user),
    controller: WorkController = Depends(get_work_controller)
):
    return await controller.create_task(current_user["emp_id"], task_in)

@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    controller: WorkController = Depends(get_work_controller)
):
    tasks = await controller.list_tasks(skip, limit)
    return {
        "total": len(tasks),
        "items": tasks
    }

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskCreate,
    current_user: dict = Depends(get_current_user), # 📍 추가: 인증 정보 주입
    controller: WorkController = Depends(get_work_controller)
):
    # 서비스 계층에서 검증할 수 있도록 current_user 전달
    return await controller.update_task(task_id, task_in, current_user)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user), # 📍 추가: 인증 정보 주입
    controller: WorkController = Depends(get_work_controller)
):
    """업무 삭제 엔드포인트"""
    # 서비스 계층에서 검증할 수 있도록 current_user 전달
    await controller.delete_task(task_id, current_user)
    return None