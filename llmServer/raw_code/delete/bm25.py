
# ==========================================
# RAG 조회 헬퍼 함수 (리랭킹 강화 버전)
# ==========================================
import hashlib
from datetime import datetime



# ── 하이브리드 검색용 BM25 인덱스 (앱 시작 시 1회 구축) ──────
_bm25_index = None
_bm25_docs  = []
_bm25_metas = []


def _build_bm25_index():
    """fewshot 컬렉션 전체를 BM25 인덱스로 구축"""
    global _bm25_index, _bm25_docs, _bm25_metas
    coll = rag_colls.get("fewshot")
    if not coll:
        return
    try:
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            import subprocess, sys
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "rank-bm25"],
                check=True,
            )
            from rank_bm25 import BM25Okapi

        all_data    = coll.get()
        _bm25_docs  = all_data["documents"]
        _bm25_metas = all_data["metadatas"]
        tokenized   = [doc.split() for doc in _bm25_docs]
        _bm25_index = BM25Okapi(tokenized)
        logger.info(f"BM25 인덱스 구축 완료: {len(_bm25_docs)}개")
    except ImportError:
        logger.warning("rank_bm25 미설치 → pip install rank-bm25")
    except Exception:
        logger.exception("BM25 인덱스 구축 실패")


# 시작 시 1회 실행
_build_bm25_index()
# 리랭커도 미리 로드 (첫 쿼리 지연 방지)
_load_reranker()