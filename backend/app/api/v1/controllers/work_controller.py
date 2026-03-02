# controllers/work_controller.py
from app.services.work_service import WorkService
from app.schemas.work import TaskCreate, TaskResponse

class WorkController:
    def __init__(self, service: WorkService):
        self.service = service

    async def create_task(self, emp_id: str, task_in: TaskCreate) -> TaskResponse:
        return await self.service.create_new_task(emp_id, task_in)

    async def list_tasks(self, skip: int, limit: int):
        return await self.service.get_work_list(skip, limit)

    # 📍 수정: current_user 인자 추가 및 서비스로 전달
    async def update_task(self, task_id: int, task_in: TaskCreate, current_user: dict) -> TaskResponse:
        return await self.service.update_existing_task(task_id, task_in, current_user)

    # 📍 수정: current_user 인자 추가 및 서비스로 전달
    async def delete_task(self, task_id: int, current_user: dict) -> bool:
        """서비스 레이어에 업무 삭제 위임 (권한 정보 포함)"""
        return await self.service.delete_task_by_id(task_id, current_user)