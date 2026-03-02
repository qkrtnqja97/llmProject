# app/schemas/work.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class TaskBase(BaseModel):
    title: str
    content: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    due_date: Optional[datetime] = None
    status: str = "todo"

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    """API 응답 시 사용하는 규격 (작성자 정보 포함)"""
    id: int
    emp_id: str
    author_name: Optional[str] = None
    team: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    """목록 조회 응답 규격"""
    total: int
    items: List[TaskResponse]