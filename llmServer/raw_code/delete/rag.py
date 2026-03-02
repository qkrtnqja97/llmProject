# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1) Few-shot 검색 (하이브리드 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_fewshot(question: str, n: int = 3) -> str:
    """하이브리드 검색 (벡터 + BM25) → 리랭킹 → 상위 n개 Few-shot 예시"""
    coll = rag_colls.get("fewshot")
    if not coll:
        return ""
    try:
        total   = coll.count()
        fetch_n = min(n * 5, total)  # 리랭킹용 후보를 넉넉히 확보

        # ── 1단계: 벡터 검색 ──
        vec_res   = coll.query(query_texts=[question], n_results=fetch_n)
        vec_docs  = vec_res["documents"][0]
        vec_metas = vec_res["metadatas"][0]
        vec_dists = vec_res["distances"][0]
        vec_scores = {doc: 1 - dist for doc, dist in zip(vec_docs, vec_dists)}

        # ── 2단계: BM25 키워드 검색 ──
        bm25_scores = {}
        bm25_meta_map = {}
        if _bm25_index is not None:
            tokens    = question.split()
            scores    = _bm25_index.get_scores(tokens)
            top_idx   = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:fetch_n]
            max_score = max(scores) if max(scores) > 0 else 1
            for i in top_idx:
                if scores[i] > 0:
                    bm25_scores[_bm25_docs[i]]   = scores[i] / max_score
                    bm25_meta_map[_bm25_docs[i]]  = _bm25_metas[i]

        # ── 3단계: 1차 점수 병합 (벡터 0.6 + BM25 0.4) ──
        # doc→meta 통합 맵
        doc_meta_map = {}
        for doc, meta in zip(vec_docs, vec_metas):
            doc_meta_map[doc] = meta
        doc_meta_map.update(bm25_meta_map)

        all_docs = set(vec_docs) | set(bm25_scores.keys())
        merged = {}
        for doc in all_docs:
            v = vec_scores.get(doc, 0)
            b = bm25_scores.get(doc, 0)
            merged[doc] = v * 0.6 + b * 0.4

        # 1차 후보: 상위 n*3개 (리랭커 입력용)
        pre_top = sorted(merged, key=merged.get, reverse=True)[:n * 3]
        pre_docs  = pre_top
        pre_metas = [doc_meta_map.get(d, {}) for d in pre_top]

        # ── 4단계: 크로스인코더 리랭킹 ──
        final_docs, final_metas = _rerank(question, pre_docs, pre_metas, top_n=n)

        # ── 5단계: 결과 포맷 ──
        examples = []
        for doc, meta in zip(final_docs, final_metas):
            sql = meta.get("sql", "")
            if sql:
                examples.append(f"Q: {doc}\nSQL: {sql}")

        logger.debug(f"Fewshot 리랭킹 결과: {[d[:30] for d in final_docs]}")
        return "\n---\n".join(examples)

    except Exception:
        logger.exception("Few-shot 하이브리드+리랭킹 실패 → 벡터 폴백")
        try:
            res = coll.query(query_texts=[question], n_results=min(n, coll.count()))
            return "\n---\n".join(
                [f"Q: {d}\nSQL: {m['sql']}"
                 for d, m in zip(res["documents"][0], res["metadatas"][0])]
            )
        except Exception:
            return ""




# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3) 비즈니스 용어 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_bizterm(question: str, n: int = 3) -> str:
    """비즈니스 용어: 후보 8개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("bizterm")
    if not coll:
        return ""
    try:
        fetch_n = min(8, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        terms = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score > 0.25:
                terms.append(f"{doc}: {meta['desc']}")

        return "\n".join(terms) if terms else ""
    except Exception:
        logger.exception("비즈니스 용어 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4) 스키마 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_schema(question: str, n: int = 3) -> str:
    """관련 테이블 스키마: 후보 8개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("schema")
    if not coll:
        return ""
    try:
        fetch_n = min(8, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, score in zip(final_docs, final_scores):
            if score > 0.2:
                hints.append(doc)

        return "\n".join(hints) if hints else ""
    except Exception:
        logger.exception("스키마 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5) 에러 패턴 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_error_hint(error_msg: str, n: int = 3) -> str:
    """에러 해결 힌트: 후보 6개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("error")
    if not coll:
        return ""
    try:
        fetch_n = min(6, coll.count())
        res = coll.query(query_texts=[error_msg], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            error_msg, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, score in zip(final_docs, final_scores):
            if score > 0.2:
                hints.append(doc)

        return "\n".join(hints) if hints else ""
    except Exception:
        logger.exception("에러 패턴 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6) 키워드 의도 검색 (벡터 + 리랭킹)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def rag_retrieve_keyword_intent(question: str, n: int = 3) -> str:
    """키워드→의도 매핑: 후보 6개 → 리랭킹 → 상위 n개 반환"""
    coll = rag_colls.get("keyword")
    if not coll:
        return ""
    try:
        fetch_n = min(6, coll.count())
        res = coll.query(query_texts=[question], n_results=fetch_n)
        if not res["documents"][0]:
            return ""

        cand_docs  = res["documents"][0]
        cand_metas = res["metadatas"][0]

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, cand_docs, cand_metas, top_n=n
        )

        hints = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score > 0.2:
                hints.append(
                    f"의도: {meta.get('intent','?')} | 주테이블: {meta.get('table','?')}"
                )

        return "\n".join(hints) if hints else ""
    except Exception:
        logger.exception("키워드 의도 리랭킹 조회 실패")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7) Fewshot 품질관리 저장 (변경 없음)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def save_successful_sql(question: str, sql: str,
                        was_retried: bool = False, retry_count: int = 0):
    """재시도 후 성공한 SQL만 저장. 유사도 0.95 이상 중복 제거.
    200개 초과 시 오래된 것 자동 정리. 저장 후 BM25 인덱스 갱신."""
    coll = rag_colls.get("fewshot")
    if not coll:
        return
    if not was_retried:
        return
    try:
        res = coll.query(query_texts=[question], n_results=1)
        if res["distances"] and res["distances"][0]:
            similarity = 1 - res["distances"][0][0]
            if similarity >= 0.95:
                logger.info(f"Fewshot 중복 스킵 (유사도 {similarity:.3f}): {question[:30]}")
                return

        doc_id = "managed_" + hashlib.md5(question.encode()).hexdigest()[:10]
        meta = {
            "sql": sql,
            "saved_at": datetime.now().isoformat(),
            "retry_count": retry_count,
            "version": 1,
        }
        existing = coll.get(ids=[doc_id])
        if existing["ids"]:
            old_ver = existing["metadatas"][0].get("version", 1)
            meta["version"] = old_ver + 1
            coll.update(ids=[doc_id], documents=[question], metadatas=[meta])
        else:
            coll.add(documents=[question], metadatas=[meta], ids=[doc_id])

        # 200개 초과 시 오래된 것 정리
        if coll.count() > 200:
            all_data = coll.get(include=["metadatas"])
            items = sorted(
                zip(all_data["ids"], all_data["metadatas"]),
                key=lambda x: x[1].get("saved_at", ""),
            )
            to_del = [id_ for id_, _ in items[: coll.count() - 200]]
            if to_del:
                coll.delete(ids=to_del)
                logger.info(f"Fewshot 정리: {len(to_del)}개 삭제")

        # BM25 인덱스 갱신
        _build_bm25_index()

        logger.info(
            f"Fewshot 저장 (재시도 {retry_count}회 후 v{meta['version']}): {question[:30]}"
        )
    except Exception:
        logger.exception("Fewshot 품질관리 저장 실패")