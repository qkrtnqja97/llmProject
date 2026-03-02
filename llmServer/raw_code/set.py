  # ==========================================
    # RAG: 구글드라이브에서 로드 (rag_builder.ipynb에서 미리 구축)
    # ==========================================
    rag_colls = {
        "fewshot": None,
        "synonym": None,
        "bizterm": None,
        "entity": None,
        "schema": None,
        "error": None,
        "keyword": None,
    }
    try:
        if not os.path.exists(DRIVE_CHROMA_PATH):
            logger.warning(
                "RAG 드라이브 경로 없음. rag_builder.ipynb를 먼저 실행하세요."
            )
            raise FileNotFoundError(f"드라이브 경로 없음: {DRIVE_CHROMA_PATH}")

        # 드라이브 → 로컬 복사 (IO 속도 개선)
        if os.path.exists(LOCAL_CHROMA_PATH):
            shutil.rmtree(LOCAL_CHROMA_PATH)
        shutil.copytree(DRIVE_CHROMA_PATH, LOCAL_CHROMA_PATH)

        chroma_client = chromadb.PersistentClient(path=LOCAL_CHROMA_PATH)
        emb = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )

        def safe_get(name):
            try:
                return chroma_client.get_collection(name, embedding_function=emb)
            except Exception:
                logger.warning(f"컬렉션 없음 (무시): {name}")
                return None

        rag_colls = {
            "fewshot": safe_get(COLL_FEWSHOT),
            "synonym": safe_get(COLL_SYNONYM),
            "bizterm": safe_get(COLL_BIZTERM),
            "entity": safe_get("entity_store"),
            "schema": safe_get(COLL_SCHEMA),
            "error": safe_get(COLL_ERROR),
            "keyword": safe_get(COLL_KEYWORD),
        }
        counts = {k: v.count() for k, v in rag_colls.items()}
        logger.info(f"RAG 로드 완료: {counts}")

    except Exception:
        logger.exception(
            "RAG 로드 실패 → RAG 없이 실행됩니다 (rag_builder.ipynb 먼저 실행 필요)"
        )

    return db, llm, entity_cache, engine, rag_colls, data_stats, schema_ctx, column_map


db, llm, entity_cache, engine, rag_colls, data_stats, schema_ctx, COLUMN_MAP = (
    get_resources()
)
