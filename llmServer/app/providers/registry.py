# llmServer/app/provider/registry.py

import logging
from typing import Dict

from app.providers.llm.base import BaseLLMProvider
from app.core.logging.logging_tags import LogTag
from app.core.logging.request_context import get_request_id

logger = logging.getLogger(__name__)

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}

    def register(self, model_name: str, provider: BaseLLMProvider):
        self._providers[model_name] = provider

        logger.info(
            "Provider registered",
            extra={
                "tag": LogTag.ROUTER,
                "model": model_name,
            },
        )
       

    def get_llm(self, model_name: str) -> BaseLLMProvider:
        if model_name not in self._providers:
            logger.error(
                "Model not registered",
                extra={
                    "tag": LogTag.ROUTER,
                    "request_id": request_id,
                    "model": model_name,
                },
            )
            raise ValueError(f"Model '{model_name}' not registered")
        
        logger.info(
            "Provider selected",
            extra={
                "tag": LogTag.ROUTER,
                "request_id": request_id,
                "model": model_name,
            },
        )
        
        return self._providers[model_name]