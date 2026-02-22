# llmServer/app/provider/registry.py

from typing import Dict
from app.providers.llm.base import BaseLLMProvider


class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}

    def register(self, model_name: str, provider: BaseLLMProvider):
        self._providers[model_name] = provider

    def get_llm(self, model_name: str) -> BaseLLMProvider:
        if model_name not in self._providers:
            raise ValueError(f"Model '{model_name}' not registered")
        return self._providers[model_name]