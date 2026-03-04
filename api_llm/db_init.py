# -*- coding: utf-8 -*-
"""
독립적 DB 연결 초기화
Streamlit 여부와 관계없이 자동으로 실행됨
"""

import sys
import logging
from typing import Dict, Tuple
from pathlib import Path

# Windows PowerShell UTF-8 지원
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 경로 설정 (상대 import 경로 수정)
api_llm_path = Path(__file__).parent
if str(api_llm_path) not in sys.path:
    sys.path.insert(0, str(api_llm_path))

logger = logging.getLogger(__name__)

# Streamlit 환경 감지
try:
    import streamlit as st
    IS_STREAMLIT = True
except:
    IS_STREAMLIT = False

# 전역 상태
_initialized = False
_resources = None


def initialize_databases() -> Dict:
    """
    PostgreSQL과 ChromaDB 자동 초기화
    
    Returns:
        {
            'db_manager': DatabaseManager,
            'chroma_manager': ChromaDBManager,
            'status': '✅ 연결 완료' 또는 '❌ 연결 실패'
        }
    """
    global _initialized, _resources
    
    if _initialized and _resources:
        logger.debug("데이터베이스가 이미 초기화됨")
        return _resources
    
    # 로거에만 출력 (Streamlit에서 print 제거)
    msg = "="*60
    logger.info(msg)
    
    msg = "데이터베이스 초기화 시작"
    logger.info(msg)
    
    msg = "="*60
    logger.info(msg)
    
    try:
        # 1. PostgreSQL 연결
        msg = "\n[1/2] PostgreSQL 연결 중..."
        logger.info(msg)
        
        try:
            from api_llm.sql.sql_executor import get_database_manager
            db_manager = get_database_manager()
            msg = "  ✅ PostgreSQL 연결 성공"
            logger.info(msg)
                
        except Exception as e:
            msg = f"  ⚠️  PostgreSQL 연결 실패: {str(e)[:100]}"
            logger.warning(msg)
            db_manager = None
        
        # 2. ChromaDB 연결
        msg = "\n[2/2] ChromaDB 연결 중..."
        logger.info(msg)
        
        try:
            from api_llm.models.vector_db import get_chroma_manager
            chroma_manager = get_chroma_manager()
            collections = chroma_manager.get_all_collections()
            msg = f"  ✅ ChromaDB 연결 성공 ({len(collections)}개 컬렉션)"
            logger.info(msg)
        except Exception as e:
            msg = f"  ⚠️  ChromaDB 연결 실패: {str(e)[:100]}"
            logger.warning(msg)
            chroma_manager = None
        
        msg = "\n" + "="*60
        logger.info(msg)
        
        if db_manager and chroma_manager:
            msg = "✅ 모든 데이터베이스 연결 완료"
            logger.info(msg)
            status = "✅ 연결 완료"
        else:
            msg = "⚠️  일부 데이터베이스 연결 실패"
            logger.warning(msg)
            status = "⚠️  부분 연결"
        
        msg = "="*60 + "\n"
        logger.info(msg)
        
        _resources = {
            'db_manager': db_manager,
            'chroma_manager': chroma_manager,
            'status': status,
        }
        
        _initialized = True
        return _resources
    
    except Exception as e:
        msg = f"데이터베이스 초기화 오류: {e}"
        logger.exception(msg)
        _resources = {
            'db_manager': None,
            'chroma_manager': None,
            'status': "❌ 연결 실패"
        }
        _initialized = True
        return _resources


def get_initialized_resources() -> Dict:
    """초기화된 리소스 반환"""
    global _resources
    if not _initialized:
        return initialize_databases()
    return _resources


# 모듈 로드 시 자동 초기화 (옵션)
# initialize_databases()
