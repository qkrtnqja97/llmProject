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
            f"{self.base_url}/v1/llm/chat/generate",
            json={"prompt": prompt},
        )
        res.raise_for_status()
        return res.json()

    async def health(self) -> bool:
        try:
            res = await self.client.get(
                f"{self.base_url}/health",
                timeout=3.0,  # 헬스체크는 짧게
            )
            return res.status_code == 200
        except Exception:
            return False
