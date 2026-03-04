# -*- coding: utf-8 -*-
"""
쿼리 캐싱 모듈
- 중복 쿼리 결과 캐싱
- TTL 기반 만료
- 캐시 무효화
"""

import hashlib
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from api_llm.config import CACHE_CONFIG

logger = logging.getLogger(__name__)


class QueryCache:
    """쿼리 결과 캐시 (세션 기반)"""

    def __init__(self, ttl_minutes: int = 30, max_size: int = 50):
        self.ttl = ttl_minutes
        self.max_size = max_size
        self.cache: Dict[str, Dict] = {}

    def _normalize_question(self, q: str) -> str:
        """질문 정규화"""
        q = q.strip().lower()
        q = re.sub(r'\s+', ' ', q)  # 공백 정규화
        q = re.sub(r'\b(\d{2})년\b', lambda m: f"20{m.group(1)}년", q)  # 연도 정규화
        return q

    def _get_cache_key(self, question: str) -> str:
        """캐시 키 생성"""
        normalized = self._normalize_question(question)
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, question: str) -> Optional[Dict[str, Any]]:
        """
        캐시에서 결과 조회
        
        Returns:
            캐시된 결과 또는 None
        """
        key = self._get_cache_key(question)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        cached_at = datetime.fromisoformat(entry["cached_at"])
        
        # TTL 확인
        if datetime.now() - cached_at > timedelta(minutes=self.ttl):
            del self.cache[key]
            logger.debug(f"캐시 만료: {question[:40]}")
            return None
        
        logger.info(f"✅ 캐시 HIT: {question[:40]}")
        return entry["result"]

    def save(self, question: str, result: Dict[str, Any]) -> None:
        """
        결과를 캐시에 저장
        
        Args:
            question: 사용자 질문
            result: 쿼리 결과
        """
        key = self._get_cache_key(question)
        self.cache[key] = {
            "result": result,
            "cached_at": datetime.now().isoformat(),
            "question": question,
        }
        
        # 캐시 크기 초과 시 오래된 것 삭제
        if len(self.cache) > self.max_size:
            oldest = min(self.cache, key=lambda k: self.cache[k]["cached_at"])
            del self.cache[oldest]
            logger.debug(f"캐시 크기 초과 → 가장 오래된 항목 삭제")

    def invalidate(self, pattern: str = "") -> None:
        """
        캐시 무효화
        
        Args:
            pattern: 패턴 (빈 문자열이면 전체 삭제)
        """
        if not pattern:
            self.cache.clear()
            logger.info("캐시 전체 초기화")
            return
        
        to_del = [k for k, v in self.cache.items() if pattern in v.get("question", "")]
        for k in to_del:
            del self.cache[k]
        logger.info(f"캐시 무효화 {len(to_del)}건 (패턴: {pattern})")

    def get_stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        return {
            "size": len(self.cache),
            "ttl_minutes": self.ttl,
            "max_size": self.max_size,
        }


# 기본 캐시 인스턴스
_default_cache = None


def get_query_cache() -> QueryCache:
    """기본 쿼리 캐시 반환"""
    global _default_cache
    if _default_cache is None:
        _default_cache = QueryCache(
            ttl_minutes=CACHE_CONFIG["TTL_MINUTES"],
            max_size=CACHE_CONFIG["MAX_SIZE"],
        )
    return _default_cache


def cache_get(question: str) -> Optional[Dict]:
    """편의 함수: 캐시 조회"""
    if not CACHE_CONFIG["ENABLE"]:
        return None
    return get_query_cache().get(question)


def cache_save(question: str, result: Dict) -> None:
    """편의 함수: 캐시 저장"""
    if not CACHE_CONFIG["ENABLE"]:
        return
    get_query_cache().save(question, result)


def cache_invalidate(pattern: str = "") -> None:
    """편의 함수: 캐시 무효화"""
    get_query_cache().invalidate(pattern)


# ==========================================
# RAG 검색 결과 캐싱
# ==========================================

class RAGCache:
    """RAG 검색 결과 캐시 (임베딩 캐싱용)"""
    
    def __init__(self, ttl_minutes: int = 60, max_size: int = 100):
        self.ttl = ttl_minutes
        self.max_size = max_size
        self.cache: Dict[str, Dict] = {}
    
    def _normalize_query(self, q: str) -> str:
        """검색 쿼리 정규화"""
        q = q.strip().lower()
        q = re.sub(r'\s+', ' ', q)  # 공백 정규화
        q = re.sub(r'[,.!?;:\'"]', '', q)  # 기호 제거
        return q
    
    def _get_cache_key(self, query: str) -> str:
        """캐시 키 생성"""
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        캐시에서 RAG 결과 조회
        
        Returns:
            캐시된 RAG 결과 또는 None
        """
        key = self._get_cache_key(query)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        cached_at = datetime.fromisoformat(entry["cached_at"])
        
        # TTL 확인
        if datetime.now() - cached_at > timedelta(minutes=self.ttl):
            del self.cache[key]
            logger.debug(f"RAG 캐시 만료: {query[:40]}")
            return None
        
        logger.info(f"⚡ RAG 캐시 HIT: {query[:40]}")
        return entry["result"]
    
    def save(self, query: str, result: Dict[str, Any]) -> None:
        """
        RAG 결과를 캐시에 저장
        
        Args:
            query: 검색 쿼리
            result: RAG 검색 결과
        """
        key = self._get_cache_key(query)
        self.cache[key] = {
            "result": result,
            "cached_at": datetime.now().isoformat(),
            "query": query,
        }
        
        # 캐시 크기 초과 시 오래된 것 삭제
        if len(self.cache) > self.max_size:
            oldest = min(self.cache, key=lambda k: self.cache[k]["cached_at"])
            del self.cache[oldest]
            logger.debug(f"RAG 캐시 크기 초과 → 가장 오래된 항목 삭제")
    
    def invalidate(self, pattern: str = "") -> None:
        """RAG 캐시 무효화"""
        if not pattern:
            self.cache.clear()
            logger.info("RAG 캐시 전체 초기화")
            return
        
        to_del = [k for k, v in self.cache.items() if pattern in v.get("query", "")]
        for k in to_del:
            del self.cache[k]
        logger.info(f"RAG 캐시 무효화 {len(to_del)}건 (패턴: {pattern})")
    
    def get_stats(self) -> Dict[str, int]:
        """RAG 캐시 통계 반환"""
        return {
            "size": len(self.cache),
            "ttl_minutes": self.ttl,
            "max_size": self.max_size,
        }


# 기본 RAG 캐시 인스턴스
_rag_cache = None


def get_rag_cache() -> RAGCache:
    """기본 RAG 캐시 반환"""
    global _rag_cache
    if _rag_cache is None:
        _rag_cache = RAGCache(
            ttl_minutes=CACHE_CONFIG.get("RAG_TTL_MINUTES", 60),
            max_size=CACHE_CONFIG.get("RAG_CACHE_SIZE", 100),
        )
    return _rag_cache


def rag_cache_get(query: str) -> Optional[Dict]:
    """편의 함수: RAG 캐시 조회"""
    if not CACHE_CONFIG.get("ENABLE_RAG_CACHE", True):
        return None
    return get_rag_cache().get(query)


def rag_cache_save(query: str, result: Dict) -> None:
    """편의 함수: RAG 캐시 저장"""
    if not CACHE_CONFIG.get("ENABLE_RAG_CACHE", True):
        return
    get_rag_cache().save(query, result)


def rag_cache_invalidate(pattern: str = "") -> None:
    """편의 함수: RAG 캐시 무효화"""
    get_rag_cache().invalidate(pattern)


def rag_cache_stats() -> Dict:
    """RAG 캐시 통계 반환"""
    return get_rag_cache().get_stats()


def cache_stats() -> Dict:
    """캐시 통계 반환"""
    return {
        "query_cache": get_query_cache().get_stats(),
        "rag_cache": get_rag_cache().get_stats(),
    }
