import hashlib
from datetime import datetime


class FewshotManager:

    def __init__(self, vector_repository, bm25_index=None):
        self.vector_repository = vector_repository
        self.bm25 = bm25_index

    async def save_successful_sql(
        self,
        question: str,
        sql: str,
        embedding: list,
        retry_count: int,
    ):

        # 🔹 1️⃣ 유사도 중복 방지
        existing = await self.vector_repository.search_by_text(
            collection_name="fewshot_sql",
            query_text=question,
            top_k=1,
        )

        if existing:
            similarity = 1 - existing[0][2]
            if similarity >= 0.95:
                return

        # 🔹 2️⃣ ID 생성
        doc_id = "managed_" + hashlib.md5(
            question.encode()
        ).hexdigest()[:10]

        # 🔹 3️⃣ 기존 버전 확인
        data = await self.vector_repository.get_all("fewshot_sql")

        version = 1
        if data.get("ids"):
            for i, id_ in enumerate(data["ids"]):
                if id_ == doc_id:
                    version = (
                        data["metadatas"][i].get("version", 1) + 1
                    )
                    break

        # 🔹 4️⃣ Insert
        await self.vector_repository.insert(
            collection_name="fewshot_sql",
            ids=[doc_id],
            embeddings=[embedding],
            documents=[question],
            metadatas=[{
                "sql": sql,
                "retry_count": retry_count,
                "version": version,
                "saved_at": datetime.utcnow().isoformat(),
            }],
        )

        # 🔹 5️⃣ 200개 유지 정책
        total = await self.vector_repository.count("fewshot_sql")

        if total > 200:

            data = await self.vector_repository.get_all("fewshot_sql")
            items = list(zip(
                data["ids"],
                data["metadatas"],
            ))

            items.sort(
                key=lambda x: x[1].get("saved_at", "")
            )

            delete_ids = [
                id_ for id_, _
                in items[: total - 200]
            ]

            await self.vector_repository.delete(
                "fewshot_sql",
                delete_ids
            )

        # 🔹 6️⃣ BM25 재빌드
        if self.bm25:
            await self.bm25.rebuild()