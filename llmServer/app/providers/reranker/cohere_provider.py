import logging
from typing import List
import cohere
from app.providers.reranker.base import BaseRerankerProvider

logger = logging.getLogger(__name__)


class CohereRerankerProvider(BaseRerankerProvider):

    def __init__(self, api_key: str, model_name: str = "rerank-v3.5"):
        self.model_name = model_name
        self.client = cohere.ClientV2(api_key)
        logger.info(f"Cohere Reranker initialized with model: {self.model_name}")

    def score(self, query: str, docs: List[str]) -> List[float]:

        if not docs:
            return []

        try:
            response = self.client.rerank(
                model=self.model_name,
                query=query,
                documents=docs,
                top_n=len(docs),  # 전부 점수 받기
            )

            # Cohere는 이미 정렬된 결과를 반환함.
            # 우리는 "원본 docs 순서에 맞는 score 리스트"가 필요하다.
            scores = [0.0] * len(docs)

            for result in response.results:
                scores[result.index] = result.relevance_score

            return scores

        except Exception as e:
            logger.error(f"Cohere Reranking API error: {e}")
            # 실패 시 neutral score 반환
            return [1.0] * len(docs)