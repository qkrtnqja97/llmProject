# llmServer/services/rerank_service.py

# app/services/rerank_service.py

class RerankService:

    def __init__(self, reranker):
        self.reranker = reranker

    def rerank(
        self,
        query: str,
        docs: list[str],
        metas: list[dict],
        top_n: int = 3,
        with_scores: bool = False,
    ):
        if not docs:
            return ([], [], []) if with_scores else ([], [])

        try:
            scores = self.reranker.score(query, docs)

            ranked = sorted(
                zip(scores, docs, metas),
                key=lambda x: x[0],
                reverse=True,
            )

            top = ranked[:top_n]

            final_docs = [d for s, d, m in top]
            final_metas = [m for s, d, m in top]
            final_scores = [s for s, d, m in top]

            if with_scores:
                return final_docs, final_metas, final_scores
            return final_docs, final_metas

        except Exception:
            # fallback 정책
            fallback_docs = docs[:top_n]
            fallback_metas = metas[:top_n]
            fallback_scores = [1.0] * len(fallback_docs)

            if with_scores:
                return fallback_docs, fallback_metas, fallback_scores
            return fallback_docs, fallback_metas