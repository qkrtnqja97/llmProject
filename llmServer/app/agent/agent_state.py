# app/graph/agent_state.py

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):

    # 입력
    user_id: str
    session_id: str
    question: str

    # Memory
    refined_question: str
    structured_memory: Dict

    # Entity
    synonym_hint: str

    # Router
    intent: str

    # SQL
    sql_query: str

    # DB 실행
    rows: List[Dict]
    df: Any                     # pandas.DataFrame (ResultValidation / Visualization 용)
    db_result: str
    explain_meta: Dict

    # Validation
    result_anomalies: List[str]

    # 시각화
    chart_info: Optional[Dict]  # Recharts 호환 차트 메타데이터

    # Retry 관련
    retry_count: int
    error_history: List[str]
    retry_strategy: str
    error_type: str

    # 최종 출력
    final_answer: str