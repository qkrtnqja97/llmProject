# -*- coding: utf-8 -*-
"""
에이전트 상태 정의
LangGraph에서 사용되는 AgentState 타입
"""

from typing import TypedDict, List, Dict, Optional, Any


class AgentState(TypedDict, total=False):
    """
    LangGraph 에이전트의 상태 객체
    
    각 노드에서 상태를 업데이트하면서 파이프라인을 진행
    """
    
    # 입력 및 기본 정보
    question: str
    refined_question: str
    synonym_hint: str
    intent: str  # INVENTORY, TECH_SALES, CHIT_CHAT
    
    # 맥락 정보 (대화 히스토리)
    context: List[Dict]  # ← 최근 대화 맥락
    
    # SQL 관련
    sql_query: str
    db_result: Any
    
    # 데이터
    df: Any  # pandas.DataFrame
    
    # 시각화
    chart_info: Dict
    
    # 에러 처리
    error_history: List[str]
    retry_count: int
    
    # [쿼리 플래너]
    query_plan: Dict  # 구조화된 쿼리 계획
    
    # [동적 스키마]
    selected_schema: str
    
    # [정적 검증]
    validation_errors: List[str]
    retry_strategy: str
    
    # [결과 검증]
    result_anomalies: List[str]
    
    # [구조화 메모리]
    structured_memory: Dict
    
    # [캐싱]
    cache_hit: bool
    cache_key: str
    
    # [설명]
    explain_meta: Dict
