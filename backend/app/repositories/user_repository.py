import asyncpg

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_user_by_emp_id(self, emp_id: str):
        """사원 번호로 유저 정보 조회 (Raw SQL)"""
        query = "SELECT emp_id, password, name, role, team FROM users.user_info WHERE emp_id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, emp_id)

    async def create_user(self, emp_id: str, hashed_password: str, name: str, role: str, team: str):
        """신규 유저 생성 (AuthService.register_user용)"""
        query = """
            INSERT INTO users.user_info (emp_id, password, name, role, team)
            VALUES ($1, $2, $3, $4, $5)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, emp_id, hashed_password, name, role, team)
            
    async def get_user_settings(self, emp_id: str):
        """사용자 설정 조회"""
        query = """
            SELECT theme, start_page as "startPage", menu_config as "sidebarMenus"
            FROM users.user_settings WHERE emp_id = $1
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, emp_id)

    async def upsert_user_settings(self, emp_id: str, theme: str, start_page: str, menu_config: str):
        """사용자 설정 저장 또는 업데이트 (Upsert)"""
        query = """
            INSERT INTO users.user_settings (emp_id, theme, start_page, menu_config)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (emp_id) 
            DO UPDATE SET 
                theme = EXCLUDED.theme,
                start_page = EXCLUDED.start_page,
                menu_config = EXCLUDED.menu_config,
                updated_at = CURRENT_TIMESTAMP
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, emp_id, theme, start_page, menu_config)