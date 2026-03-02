# app/services/work_service.py
from fastapi import HTTPException, status
from app.repositories.work_repository import WorkRepository
from app.schemas.work import TaskCreate

class WorkService:
    def __init__(self, work_repo: WorkRepository):
        self.work_repo = work_repo

    async def create_new_task(self, emp_id: str, task_in: TaskCreate): 
        return await self.work_repo.create_task(emp_id, task_in)
    
    async def get_work_list(self, skip: int, limit: int):
        # 💡 나중에 '팀별 조회' 기능을 넣으려면 여기에 user_team 파라미터를 추가하여 필터링할 수 있습니다.
        return await self.work_repo.get_tasks(skip, limit)
    
    async def update_existing_task(self, task_id: int, task_in: TaskCreate, current_user: dict):
        """업무 수정 시 권한 검증 추가"""
        task = await self.work_repo.get_task_by_id(task_id) # 해당 ID의 업무 조회 필요
        if not task:
            raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")

        # 권한 체크: 관리자이거나 본인 업무인 경우만 허용
        if current_user['role'] != 'admin' and task['emp_id'] != current_user['emp_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="수정 권한이 없습니다."
            )
            
        return await self.work_repo.update_task(task_id, task_in)

    async def delete_task_by_id(self, task_id: int, current_user: dict):
        """업무 삭제 시 권한 검증 추가"""
        task = await self.work_repo.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")

        # 권한 체크: 관리자이거나 본인 업무인 경우만 허용
        if current_user['role'] != 'admin' and task['emp_id'] != current_user['emp_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="삭제 권한이 없습니다."
            )
            
        return await self.work_repo.delete_task(task_id)