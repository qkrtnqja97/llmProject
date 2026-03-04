# -*- coding: utf-8 -*-
"""
RAG 검색 모듈
- 하이브리드 검색 (벡터 + BM25)
- 리랭킹 (크로스인코더)
- 3가지 RAG 컬렉션 검색

[컬렉션별 검색 전략 및 반환값]
- FEWSHOT   : top-N 방식 (유사도 필터 없음, 상위 N개 반환) → doc + meta 둘 다
- BIZTERM   : 유사도 임계값 방식 (SCORE_THRESHOLD_BIZTERM 이상만 반환) → doc + meta 둘 다
- SCHEMA    : 유사도 임계값 방식 (SCORE_THRESHOLD_SCHEMA 이상만 반환) → meta만
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False

from api_llm.config import RAG_CONFIG, CHROMA_COLLECTIONS, SYSTEM_CONSTANTS
from api_llm.models import get_chroma_manager
from api_llm.cache import rag_cache_get, rag_cache_save

logger = logging.getLogger(__name__)


# ==========================================
# 컬렉션별 검색 전략 설정 (config.py에서 중앙 관리)
# ※ 3단계 계층적 필터링: 병합 임계값 → 리랭킹 → 최종 선택
# ==========================================

# config에서 모든 설정값 로드
# ─── Step 1: 후보 선정 (Hybrid Score Threshold) ───
HYBRID_SCORE_THRESHOLD = RAG_CONFIG.get("HYBRID_SCORE_THRESHOLD", 0.3)
FETCH_MULTIPLIER = RAG_CONFIG.get("FETCH_MULTIPLIER", 5)

# ─── Step 2: 리랭킹 ───
RERANK_TOP_N = RAG_CONFIG.get("RERANK_TOP_N", 30)

# ─── Step 3: 최종 선택 (Reranker Score Threshold) ───
RERANKER_SCORE_THRESHOLD = RAG_CONFIG.get("RERANKER_SCORE_THRESHOLD", 0.4)

# ─── 컬렉션별 반환 상위 N개 ───
TOPN_FEWSHOT = RAG_CONFIG.get("TOPN_FINAL", 3)
TOPN_BIZTERM = RAG_CONFIG.get("TOPN_BIZTERM", 3)
TOPN_SCHEMA = RAG_CONFIG.get("TOPN_SCHEMA", 7)


# ==========================================
# 리랭커 및 BM25 전역 변수
# ==========================================

_reranker   = None

# BM25 인덱스를 컬렉션별로 관리
_bm25_indices = {
    "FEWSHOT": {"index": None, "docs": [], "metas": []},
    "BIZTERM": {"index": None, "docs": [], "metas": []},
    "SCHEMA":  {"index": None, "docs": [], "metas": []},
}


# ==========================================
# 내부 유틸 함수
# ==========================================

import os

def _load_reranker():
    """Cohere SDK 클라이언트 로드"""
    global _reranker

    if _reranker is not None:
        return _reranker

    try:
        import cohere
        cohere_api_key = os.environ.get("COHERE_API_KEY")
        if not cohere_api_key:
            logger.error("COHERE_API_KEY 환경변수가 설정되지 않았습니다.")
            return None
        
        _reranker = cohere.ClientV2(api_key=cohere_api_key)
        logger.info("✅ Cohere 클라이언트 로드 성공")
    except Exception:
        logger.exception("Cohere 클라이언트 로드 실패 → 리랭킹 없이 진행")
        _reranker = None

    return _reranker


def _rerank_with_scores(
    query: str,
    docs:  List[str],
    metas: List[dict],
    top_n: int = 10,
) -> Tuple[List[str], List[dict], List[float]]:
    """Cohere 리랭킹 + 점수 반환"""
    cohere_client = _load_reranker()

    if cohere_client is None or not docs:
        scores = [1.0] * min(top_n, len(docs))
        return docs[:top_n], metas[:top_n], scores

    try:
        # cohere.Client의 rerank 메소드 호출
        response = cohere_client.rerank(
            model=RAG_CONFIG.get("RERANKER_MODEL", "rerank-v3.5"),
            query=query,
            documents=docs,
            top_n=top_n
        )
        
        ranked_docs = []
        ranked_metas = []
        ranked_scores = []
        
        for res in response.results:
            idx = res.index
            ranked_docs.append(docs[idx])
            ranked_metas.append(metas[idx])
            ranked_scores.append(res.relevance_score)

        return ranked_docs, ranked_metas, ranked_scores

    except Exception:
        logger.exception("Cohere 리랭킹 실패")
        return docs[:top_n], metas[:top_n], [1.0] * min(top_n, len(docs))


def _query_collection(coll, question: str, fetch_n: int):
    """ChromaDB 컬렉션 공통 쿼리 헬퍼"""
    res = coll.query(query_texts=[question], n_results=fetch_n)
    docs  = res["documents"][0]  if res.get("documents") else []
    metas = res["metadatas"][0]  if res.get("metadatas") else []
    dists = res["distances"][0]  if res.get("distances")  else []
    return docs, metas, dists


def _build_bm25_indices():
    """모든 컬렉션에 대해 BM25 인덱스 구축"""
    global _bm25_indices

    if not HAS_BM25:
        logger.warning("BM25 미설치: pip install rank-bm25")
        return

    manager = get_chroma_manager()
    
    for key, coll_name in CHROMA_COLLECTIONS.items():
        try:
            coll = manager.get_collection(coll_name)
            if not coll:
                continue

            all_data = coll.get()
            docs = all_data["documents"]
            metas = all_data["metadatas"]
            
            if not docs:
                continue

            tokenized = [doc.split() for doc in docs]
            _bm25_indices[key]["index"] = BM25Okapi(tokenized)
            _bm25_indices[key]["docs"]  = docs
            _bm25_indices[key]["metas"] = metas
            logger.info(f"✅ BM25 인덱스 구축 [{key}]: {len(docs)}개 문서")

        except Exception:
            logger.exception(f"BM25 인덱스 구축 실패 [{key}]")


# 모듈 초기화
_build_bm25_indices()
_load_reranker()


# ==========================================
# RAG 검색 함수 (3가지)
# ==========================================

def _hybrid_search(coll, coll_key: str, question: str, fetch_n: int):
    """벡터 + BM25 하이브리드 검색 공통 함수 (0.6:0.4)"""
    # 1. 벡터 검색
    vec_docs, vec_metas, vec_dists = _query_collection(coll, question, fetch_n)
    vec_scores = {doc: 1 - dist for doc, dist in zip(vec_docs, vec_dists)}
    
    # 2. BM25 검색
    bm25_scores = {}
    bm25_meta_map = {}
    bm25_info = _bm25_indices.get(coll_key, {})
    bm25_index = bm25_info.get("index")
    
    if bm25_index is not None:
        tokens = question.split()
        raw = bm25_index.get_scores(tokens)
        top_idx = sorted(range(len(raw)), key=lambda i: raw[i], reverse=True)[:fetch_n]
        max_score = max(raw) if max(raw) > 0 else 1
        
        for i in top_idx:
            if raw[i] > 0:
                doc = bm25_info["docs"][i]
                bm25_scores[doc] = raw[i] / max_score
                bm25_meta_map[doc] = bm25_info["metas"][i]

    # 3. 점수 병합 및 메타데이터 맵 구축
    doc_meta_map = {doc: meta for doc, meta in zip(vec_docs, vec_metas)}
    doc_meta_map.update(bm25_meta_map)

    all_docs = set(vec_docs) | set(bm25_scores.keys())
    merged = {
        doc: vec_scores.get(doc, 0) * 0.6 + bm25_scores.get(doc, 0) * 0.4
        for doc in all_docs
    }
    
    return merged, doc_meta_map


def retrieve_fewshot(question: str) -> str:
    """
    [3단계 계층적 필터링] Few-shot SQL 예제
    - Step 1: Hybrid (Vector 0.6 + BM25 0.4)
    - Step 2: Reranking
    - Step 3: Threshold & Top-N
    """
    manager = get_chroma_manager()
    coll = manager.get_collection(CHROMA_COLLECTIONS["FEWSHOT"])
    if not coll: return ""

    try:
        fetch_n = min(TOPN_FEWSHOT * 10, coll.count())
        merged, doc_meta_map = _hybrid_search(coll, "FEWSHOT", question, fetch_n)

        # Step 1 필터링 (넉넉하게)
        candidate_docs = [doc for doc, score in merged.items() if score >= HYBRID_SCORE_THRESHOLD]
        candidate_metas = [doc_meta_map.get(d, {}) for d in candidate_docs]

        if not candidate_docs: return ""

        # Step 2: 리랭킹
        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, candidate_docs, candidate_metas, top_n=RERANK_TOP_N
        )

        # Step 3: 최종 선택
        examples = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score >= RERANKER_SCORE_THRESHOLD:
                sql = meta.get("sql", "")
                if sql:
                    examples.append(f"Q: {doc}\nSQL: {sql}")
                    if len(examples) >= TOPN_FEWSHOT: break
        
        return "\n---\n".join(examples) if examples else ""

    except Exception:
        logger.exception("Few-shot 검색 실패")
        return ""


def retrieve_bizterm(question: str, top_n: int = None, threshold: float = None) -> str:
    """
    [3단계 계층적 필터링] 비즈니스 용어
    - Step 1: Hybrid (Vector 0.6 + BM25 0.4)
    - Step 2: Reranking
    - Step 3: Threshold & Top-N
    """
    top_n = top_n or TOPN_BIZTERM
    threshold = threshold or RERANKER_SCORE_THRESHOLD
    
    manager = get_chroma_manager()
    coll = manager.get_collection(CHROMA_COLLECTIONS["BIZTERM"])
    if not coll: return ""

    try:
        fetch_n = min(top_n * FETCH_MULTIPLIER, coll.count())
        merged, doc_meta_map = _hybrid_search(coll, "BIZTERM", question, fetch_n)

        candidate_docs = [doc for doc, score in merged.items() if score >= HYBRID_SCORE_THRESHOLD]
        candidate_metas = [doc_meta_map.get(d, {}) for d in candidate_docs]

        if not candidate_docs: return ""

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, candidate_docs, candidate_metas, top_n=RERANK_TOP_N
        )

        terms = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score >= threshold:
                terms.append(f"{doc}: {meta.get('desc', '?')}")
                if len(terms) >= top_n: break
        
        return "\n".join(terms) if terms else ""

    except Exception:
        logger.exception("비즈니스 용어 검색 실패")
        return ""


def retrieve_schema(question: str, top_n: int = None, threshold: float = None) -> str:
    """
    [3단계 계층적 필터링] 테이블 스키마
    - Step 1: Hybrid (Vector 0.6 + BM25 0.4)
    - Step 2: Reranking
    - Step 3: Threshold & Top-N
    """
    top_n = top_n or TOPN_SCHEMA
    threshold = threshold or RERANKER_SCORE_THRESHOLD
    
    manager = get_chroma_manager()
    coll = manager.get_collection(CHROMA_COLLECTIONS["SCHEMA"])
    if not coll: return ""

    try:
        fetch_n = min(top_n * FETCH_MULTIPLIER, coll.count())
        merged, doc_meta_map = _hybrid_search(coll, "SCHEMA", question, fetch_n)

        candidate_docs = [doc for doc, score in merged.items() if score >= HYBRID_SCORE_THRESHOLD]
        candidate_metas = [doc_meta_map.get(d, {}) for d in candidate_docs]

        if not candidate_docs: return ""

        final_docs, final_metas, final_scores = _rerank_with_scores(
            question, candidate_docs, candidate_metas, top_n=RERANK_TOP_N
        )

        hints = []
        for doc, meta, score in zip(final_docs, final_metas, final_scores):
            if score >= threshold:
                # doc: "{id}: {description}" (유사도 검색용)
                # meta: id, columns, sql (실제 SQL 생성에 필요한 정보)
                table_id = meta.get("id", "")
                columns  = meta.get("columns", "")
                sql_hint = meta.get("sql", "")
                if table_id and columns:
                    entry = f"테이블: {table_id}\n설명: {doc}\n컬럼: {columns}"
                    if sql_hint:
                        entry += f"\n제약조건: {sql_hint}"
                else:
                    entry = doc  # 메타 없을 경우 fallback
                hints.append(entry)
                if len(hints) >= top_n: break
        
        return "\n\n".join(hints) if hints else ""

    except Exception:
        logger.exception("스키마 검색 실패")
        return ""


# ==========================================
# 병렬 RAG 실행
# ==========================================

_rag_executor = ThreadPoolExecutor(max_workers=SYSTEM_CONSTANTS["MAX_WORKERS"])


def retrieve_parallel(question: str) -> str:
    """3가지 RAG 병렬 실행 후 LLM 컨텍스트 문자열 반환 (매번 fresh 검색)"""

    def run(fn, *args):
        try:
            return fn(*args)
        except Exception:
            return ""

    # 병렬 검색
    futures = {
        "fewshot": _rag_executor.submit(run, retrieve_fewshot,        question),
        "bizterm": _rag_executor.submit(run, retrieve_bizterm,        question),
        "schema":  _rag_executor.submit(run, retrieve_schema,         question),
    }

    results = {}
    for key, fut in futures.items():
        if fut is None:
            results[key] = ""
            continue
        try:
            results[key] = fut.result(timeout=SYSTEM_CONSTANTS["THREAD_POOL_TIMEOUT"])
        except Exception:
            results[key] = ""
            logger.warning(f"RAG 타임아웃: {key}")

    # 3단계: 결과 포맷팅
    section = ""
    if results.get("fewshot"):
        section += f"\n[유사 질문-SQL 예시]\n{results['fewshot']}"
    if results.get("bizterm"):
        section += f"\n[비즈니스 용어]\n{results['bizterm']}"
    if results.get("schema"):
        section += f"\n[테이블 스키마]\n{results['schema']}"
    
    return section