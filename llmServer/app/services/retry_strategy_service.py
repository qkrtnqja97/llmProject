# app/services/retry_strategy_service.py

import re
from typing import Dict


class RetryStrategyService:

    def __init__(self, column_map: Dict):
        self.column_map = column_map

    def analyze(self, error_msg: str) -> Dict:

        if not error_msg:
            return {"strategy": None, "hint": ""}

        err_lower = error_msg.lower()

        if "does not exist" in err_lower and "column" in err_lower:
            col_match = re.search(r'column "?(\w+)"?', error_msg, re.IGNORECASE)
            missing = col_match.group(1) if col_match else None
            if not missing:
                return {"strategy": "unknown", "hint": error_msg[:300]}

            found_in = [
                t
                for t, cols in self.column_map.items()
                if missing.lower() in [c.lower() for c in cols]
            ]

            hint = f"'{missing}' 컬럼은 {found_in[0] if found_in else '알 수 없는'} 테이블 소속."
            if found_in:
                hint += f" JOIN {found_in[0]} 후 {found_in[0]}.{missing} 로 참조하세요."

            return {"strategy": "column_missing", "hint": hint}

        if "relation" in err_lower and "does not exist" in err_lower:
            tbl_match = re.search(r'relation "?(\w+)"?', error_msg, re.IGNORECASE)
            missing = tbl_match.group(1) if tbl_match else "unknown"
            return {
                "strategy": "table_missing",
                "hint": f"테이블 '{missing}' 없음. 유효 테이블: {list(self.column_map.keys())}",
            }

        if "syntax error" in err_lower:
            return {
                "strategy": "syntax",
                "hint": (
                    "SQL 단순화: TO_DATE/DATE_TRUNC 중첩 금지. "
                    "EXTRACT(YEAR FROM col)=연도 사용. "
                    "복잡한 서브쿼리는 CTE(WITH절)로 분리."
                ),
            }

        if "timeout" in err_lower or "canceling" in err_lower:
            return {
                "strategy": "timeout",
                "hint": "타임아웃: LIMIT 10으로 축소, WHERE에 날짜 범위 추가, CTE로 분리.",
            }

        if "group by" in err_lower or "aggregate" in err_lower:
            return {
                "strategy": "logic",
                "hint": "GROUP BY 오류: SELECT의 모든 비집계 컬럼을 GROUP BY에 포함하세요.",
            }

        return {"strategy": "unknown", "hint": error_msg[:300]}
