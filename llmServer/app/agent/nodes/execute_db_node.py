# llmServer/app/agent/nodes/execute_db_node.py

from typing import Dict
from app.container.container import ServiceContainer


class ExecuteDBNode:
    """
    DB 실행 노드

    역할:
    - SQL 실행
    - Static validation + Runtime 실행
    - rows / db_result / error_type 반환
    - rows → df 변환 (ResultValidationNode, VisualizationNode에서 사용)

    Graph 계약:
    - 입력: sql_query, retry_count, error_history 등
    - 출력:
        {
            "rows": List[Dict],
            "df":   pandas.DataFrame | None,
            "db_result": str,
            "retry_count": int,
            "error_type": str | None,
            "error_history": List[str],
            "explain_meta": Dict
        }
    """

    def __init__(self, container: ServiceContainer):
        self.execute_service = container.execute_db_service

    async def __call__(self, state: Dict) -> Dict:
        result = await self.execute_service.execute(state)

        # rows → DataFrame 변환 (ResultValidation / Visualization 공용)
        rows = result.get("rows")
        if rows:
            try:
                import pandas as pd
                result["df"] = pd.DataFrame(rows)
            except Exception:
                pass

        new_state = state.copy()
        new_state.update(result)
        return new_state