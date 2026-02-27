# llmServer/app/infra/rag/vector_repository


class VectorRepository:
    """
    Chroma 또는 다른 벡터 DB 접근 전용 계층.
    서비스는 이 내부 구현을 모른다.
    """

    def __init__(self, collections: dict):
        self.collections = collections

    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 3,
        with_distance: bool = False,
    ):
        coll = self.collections.get(collection_name)
        if not coll:
            return []

        try:
            res = coll.query(query_texts=[query], n_results=top_k)

            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            dists = res.get("distances", [[]])[0]

            if with_distance:
                return list(zip(docs, metas, dists))
            else:
                return list(zip(docs, metas))

        except Exception:
            return []
