# llmServer/test/providers/test_cohere_provider.py

import pytest
from app.providers.reranker.cohere_provider import CohereRerankerProvider


class FakeResult:
    def __init__(self, index, relevance_score):
        self.index = index
        self.relevance_score = relevance_score


class FakeResponse:
    def __init__(self):
        self.results = [
            FakeResult(0, 0.9),
            FakeResult(2, 0.5),
            FakeResult(1, 0.2),
        ]


class FakeClient:
    def rerank(self, **kwargs):
        return FakeResponse()


def test_cohere_score_success():

    provider = CohereRerankerProvider(api_key="fake-key")

    # Cohere 실제 클라이언트 대신 FakeClient 주입
    provider.client = FakeClient()

    docs = ["doc1", "doc2", "doc3"]

    scores = provider.score("test query", docs)

    # index 기반으로 score 매핑되는지 확인
    assert scores == [0.9, 0.2, 0.5]


def test_cohere_score_empty_docs():

    provider = CohereRerankerProvider(api_key="fake-key")
    provider.client = FakeClient()

    scores = provider.score("test query", [])

    assert scores == []


def test_cohere_score_api_failure(monkeypatch):

    class FailingClient:
        def rerank(self, **kwargs):
            raise Exception("API error")

    provider = CohereRerankerProvider(api_key="fake-key")
    provider.client = FailingClient()

    docs = ["doc1", "doc2"]

    scores = provider.score("query", docs)

    # 실패 시 fallback score
    assert scores == [1.0, 1.0]