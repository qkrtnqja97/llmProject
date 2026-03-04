# backend/app/clients/ai/llm_client.py

import httpx
from app.core.config import settings

class LLMClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.base_url = settings.LLM_SERVER_URL

    async def generate(self, prompt: str):
        target_url = f"{self.base_url}/agent/query"
        try:
            # 📍 timeout을 100초로 대폭 늘려 AI의 답변 생성을 기다려줍니다.
            res = await self.client.post(
                target_url,
                json={
                    "user_id": "test_user", 
                    "session_id": "test_session", 
                    "question": prompt
                },
                timeout=100.0  # 기본 5초 -> 100초로 변경
            )
            
            print(f'[{target_url}] 응답 상태 코드:', res.status_code)
            res.raise_for_status()
            return res.json()

        except httpx.ReadTimeout:
            print(f"❌ LLM 서버 응답 시간 초과 (Timeout): {target_url}")
            return {"response": "AI가 답변을 생성하는 데 시간이 너무 오래 걸려 연결이 끊겼습니다. 잠시 후 다시 시도해 주세요."}
        
        except httpx.ConnectError:
            print(f"❌ LLM 서버 연결 실패: {self.base_url} 주소를 찾을 수 없습니다.")
            return {"response": "AI 서버에 연결할 수 없습니다. 서버 주소 설정을 확인해 주세요."}
            
        except Exception as e:
            print(f"❌ LLM 클라이언트 에러 발생: {str(e)}")
            return {"response": f"응답 처리 중 오류가 발생했습니다: {str(e)}"}

    async def health(self) -> bool:
        try:
            res = await self.client.get(
                f"{self.base_url}/health",
                timeout=3.0,
            )
            return res.status_code == 200
        except Exception:
            return False