# etl/clients/base_embedder.py

from abc import ABC, abstractmethod


class BaseEmbedder(ABC):

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        pass