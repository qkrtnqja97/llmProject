from app.services.chat_service import ChatService

class ChatController:
    def __init__(self, service: ChatService):
        self.service = service

    async def chat_stream_generator(self, prompt: str):
        # 서비스의 chat 함수가 스트리밍을 지원하도록 구성하거나, 
        # 현재 구조에서는 단순 응답을 쪼개서 보내는 방식으로 우선 구현
        response = await self.service.chat(prompt)
        answer = response.get("response", "")
        
        # 한 글자씩 끊어서 전송 (실제 스트리밍 LLM 연동 전 임시 처리)
        for char in answer:
            yield char
            import asyncio
            await asyncio.sleep(0.01)