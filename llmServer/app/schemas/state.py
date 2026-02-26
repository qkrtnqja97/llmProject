# app/schemas/state.py

from typing import TypedDict, List, Dict, Any, Annotated
import operator

class AgentState(TypedDict):
    # 기본 입력 및 정제 결과
    question: str
    refined_question: str
    
    # 분석 및 프로세싱 데이터
    intent: str
    synonym_hint: str
    
    # 추적 및 에러 핸들링 (리스트는 Annotated를 통해 합쳐지도록 설정 가능)
    error_history: Annotated[List[str], operator.add]
    retry_count: int
    
    # 메모리 및 결과물
    structured_memory: Dict[str, Any]
    result_anomalies: List[Any]
    validation_errors: List[Any]
    
    # 최종 답변 및 시각화 데이터
    sql_query: str
    db_result: List[Dict[str, Any]]
    visual_data: Dict[str, Any]
    final_answer: str