# app/repositories/work_repository.py
import asyncpg
from datetime import datetime
from typing import List, Dict, Optional

class WorkRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_task(self, emp_id: str, task_data: any) -> dict:
        query = """
            INSERT INTO users.tasks 
            (emp_id, title, content, priority, due_date, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, emp_id, title, content, priority, status, due_date, created_at
        """
        data = task_data.model_dump() if hasattr(task_data, 'model_dump') else task_data
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                emp_id,
                data.get("title"),
                data.get("content"),
                data.get("priority"),
                data.get("due_date"),
                data.get("status")
            )
            return dict(row)
    async def get_task_by_id(self, task_id: int) -> Optional[dict]:
        """📍 추가: 권한 검증을 위한 업무 단건 조회"""
        query = "SELECT * FROM users.tasks WHERE id = $1"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, task_id)
            return dict(row) if row else None
        
    async def get_tasks(self, skip: int = 0, limit: int = 50) -> List[dict]:
        query = """
            SELECT t.*, u.name as author_name
            FROM users.tasks t
            LEFT JOIN users.user_info u ON t.emp_id = u.emp_id
            ORDER BY t.created_at DESC
            OFFSET $1 LIMIT $2
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, skip, limit)
            return [dict(r) for r in rows]
        
    async def update_task(self, task_id: int, task_data: any) -> dict:
        query = """
            UPDATE users.tasks 
            SET title = $1, content = $2, priority = $3, due_date = $4, status = $5
            WHERE id = $6
            RETURNING id, emp_id, title, content, priority, status, due_date, created_at
        """
        data = task_data.model_dump() if hasattr(task_data, 'model_dump') else task_data
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                data.get("title"),
                data.get("content"),
                data.get("priority"),
                data.get("due_date"),
                data.get("status"),
                task_id
            )
            if not row:
                raise Exception("Task not found")
            return dict(row)

    # 📍 삭제 기능 추가
    async def delete_task(self, task_id: int) -> bool:
        """업무 삭제 수행"""
        query = "DELETE FROM users.tasks WHERE id = $1"
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, task_id)
            return result != "DELETE 0"