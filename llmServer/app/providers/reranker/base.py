# llmServer/app/providers/reranker/base.py

from abc import ABC, abstractmethod
from typing import List

class BaseReranker(ABC):

    @abstractmethod
    def score(self, query: str, docs: List[str]) -> List[float]:
        """query-doc relevance score 리스트 반환"""
        pass