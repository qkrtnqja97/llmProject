# backend/app/clients/llm_client.py
# LLM 서버와 통신하기 위한 클라이언트 클래스 정의

import httpx

from app.core.config import settings

class LLMClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.base_url = settings.LLM_SERVER_URL

    async def generate(self, prompt: str):
        res = await self.client.post(
            f"{self.base_url}/agent/query",
            json={
              "user_id" : "test_user",  # 실제 서비스에서는 인증된 사용자 ID를 전달
              "session_id": "test_session",  # 실제 서비스에서는 세션 관리 로직에 따라 고유한 세션 ID를 전달  
              "question": prompt},
        )
        print(f'{self.base_url}/agent/query 응답 상태 코드:', res.status_code)
        res.raise_for_status()
        return res.json()

    async def health(self) -> bool:
        try:
            res = await self.client.get(
                f"{self.base_url}/health",
                timeout=3.0,  # 헬스체크는 짧게
            )
            print(f'{self.base_url}/agent/query 응답 상태 코드:', res.status_code)
            return res.status_code == 200
        except Exception:
            return False
