# app/services/rag_service.py

import asyncio
from app.services.retrieval.engine import RetrievalEngine
from app.services.retrieval.strategies import (
    SynonymStrategy,
    BiztermStrategy,
    SchemaStrategy,
    ErrorStrategy,
    KeywordStrategy,
)


class RAGService:

    def __init__(self, retrieval_engine: RetrievalEngine):
        self.engine = retrieval_engine

    async def build(
        self,
        question: str,
        synonym_hint: str = "",
        last_error: str = "",
    ) -> str:

        tasks = []

        tasks.append(self.engine.retrieve_fewshot(question))

        if synonym_hint:
            tasks.append(asyncio.sleep(0, result=synonym_hint))
        else:
            tasks.append(
                self.engine.retrieve(SynonymStrategy(), question)
            )

        tasks.append(
            self.engine.retrieve(BiztermStrategy(), question)
        )

        tasks.append(
            self.engine.retrieve(SchemaStrategy(), question)
        )

        if last_error:
            tasks.append(
                self.engine.retrieve(ErrorStrategy(), last_error)
            )
        else:
            tasks.append(asyncio.sleep(0, result=""))

        tasks.append(
            self.engine.retrieve(KeywordStrategy(), question)
        )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        results = [
            r if isinstance(r, str) else ""
            for r in results
        ]

        (
            fewshot,
            synonym,
            bizterm,
            schema,
            error,
            keyword,
        ) = results

        section = ""

        if fewshot:
            section += f"\n[유사 질문-SQL 예시]\n{fewshot}"
        if synonym:
            section += f"\n[동의어 정보]\n{synonym}"
        if bizterm:
            section += f"\n[비즈니스 용어 정의]\n{bizterm}"
        if schema:
            section += f"\n[관련 테이블 스키마]\n{schema}"
        if error:
            section += f"\n[에러 해결 힌트]\n{error}"
        if keyword:
            section += f"\n[질문 의도 힌트]\n{keyword}"

        return section.strip()