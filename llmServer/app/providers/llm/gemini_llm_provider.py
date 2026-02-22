# /llmServer/app/provider/llm/gemini_llm_provider.py

from google import genai
from google.genai import types
from app.providers.llm.base import BaseLLMProvider
from app.schemas.chat import ChatMessage



class GeminiLLMProvider(BaseLLMProvider):

    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model_name

    async def generate(self, messages: list[ChatMessage]):

        contents = self._convert_to_gemini(messages)

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )

        return response.text

    def _convert_to_gemini(self, messages: list[ChatMessage]):
      contents = []
      for msg in messages:
          # Gemini API용 role 변환
          role = msg.role
          if role == "system":
              role = "user"  # 시스템 메시지를 user로 넣는 방법
          elif role == "assistant":
              role = "model"

          contents.append(
              types.Content(
                  role=role,
                  parts=[types.Part(text=msg.content)]              )
          )
      return contents