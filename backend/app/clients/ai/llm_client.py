# backend/app/clients/llm_client.py
# LLM 서버와 통신하기 위한 클라이언트 클래스 정의

import httpx

from app.core.config import settings

class LLMClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.base_url = settings.LLM_SERVER_URL

    async def generate(self, user_id: str, session_id: str, prompt: str):

        try:
            res = await self.client.post(
                f"{self.base_url}/agent/query",
                json={
                    "user_id": user_id,
                    "session_id": session_id,
                    "question": prompt
                },
                timeout=120.0
            )

            res.raise_for_status()
            return res.json()

        except httpx.ReadTimeout:
            return {"response": "LLM 서버 응답이 지연되고 있습니다."}

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
