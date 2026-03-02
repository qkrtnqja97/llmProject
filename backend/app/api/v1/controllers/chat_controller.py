from app.services.chat_service import ChatService

class ChatController:
    def __init__(self, service: ChatService):
        self.service = service

    async def chat(self, prompt: str):
        return await self.service.chat(prompt)