def entity_linking_node(state: AgentState):
    q = state["question"]
    refined = q

    # 1차: rapidfuzz 기반 오타 보정
    names = entity_cache["manufacturers"] + entity_cache["vendors"]
    for word in q.split():
        if len(word) >= 2:
            match = process.extractOne(word, names, scorer=fuzz.ratio)
            if match and match[1] > 70:
                refined = refined.replace(word, match[0])

    # 2차: entity_store 벡터 검색으로 part_number 오타 보정
    coll_ent = rag_colls.get("entity")
    if coll_ent:
        try:
            res = coll_ent.query(query_texts=[q], n_results=3)
            for doc, meta, dist in zip(
                res["documents"][0], res["metadatas"][0], res["distances"][0]
            ):
                if dist < 0.15 and meta.get("type") == "part_number":
                    for word in q.split():
                        if len(word) > 5 and word.upper() != doc.upper():
                            match_score = sum(c in doc for c in word) / max(
                                len(word), len(doc)
                            )
                            if match_score > 0.8:
                                refined = refined.replace(word, doc)
                                logger.info(f"part_number 보정: {word} → {doc}")
        except Exception:
            pass

    # 3차: RAG 동의어 사전 힌트 수집
    synonym_hint = rag_retrieve_synonyms(q)
    if synonym_hint:
        logger.info(f"동의어 감지: {synonym_hint}")

    # 구조화 메모리로 대명사/생략 표현 보완
    memory = st.session_state.get("structured_memory", {})
    refined = inject_memory_to_question(refined, memory)

    return {
        "refined_question":  refined,
        "synonym_hint":      synonym_hint,
        "error_history":     [],
        "retry_count":       0,
        "structured_memory": memory,
        "result_anomalies":  [],
        "validation_errors": [],
    }
