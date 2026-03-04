# llmServer/app/agent/nodes/visualization_node.py

import re
import logging
import pandas as pd
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class VisualizationNode:
    """
    시각화 메타데이터 생성 노드

    역할:
    - 사용자 질문 + DB rows → Recharts가 직접 사용하는 chart_info 생성
    - 차트 타입 추론: bar / line / table / none
    - x축 / y축 컬럼 자동 결정 (날짜 컬럼 우선)
    - Dual Y-Axis (스케일 차이 > 10배 시) 자동 분기

    Graph 계약:
    - 입력: rows (List[Dict]), question (str)
    - 출력: {"chart_info": Dict}

    chart_info 구조 (Recharts 호환):
    {
        "type":             "bar" | "line" | "table" | "none",
        "title":            str,
        "xKey":             str,          # <XAxis dataKey="...">
        "dataKeys":         List[str],    # [<Bar dataKey="...">, ...]
        "useSecondaryAxis": bool,         # ComposedChart dual axis 여부
        "yAxes":            Dict[str, str], # {"col": "primary" | "secondary"}
        "data":             List[Dict],   # Recharts data prop에 직접 전달
    }
    """

    # 날짜 컬럼 패턴 (단어 경계 기반)
    _DT_PATTERN = re.compile(
        r'(?<![a-z])(date|year|month|day|일자|날짜|기간)(?![a-z])',
        re.IGNORECASE,
    )
    _DT_HANGUL = ["일자", "날짜", "기간", "년도", "연도"]
    _DT_KOREAN_AGGS = ["월별", "연별", "분기별", "년월", "년도", "연도"]

    # 날짜 컬럼 우선순위 (세분화 → 굵은 순)
    _PRIORITY = ["month", "day", "date", "year", "월", "일", "년", "날짜"]

    async def __call__(self, state: Dict) -> Dict:
        question = state.get("question", "")
        rows = state.get("rows") or []

        if not rows:
            new_state = state.copy()
            new_state["chart_info"] = {"type": "none"}
            return new_state

        try:
            df = pd.DataFrame(rows)
        except Exception:
            new_state = state.copy()
            new_state["chart_info"] = {"type": "none"}
            return new_state

        chart_info = self._infer(question, df)
        new_state = state.copy()
        new_state["chart_info"] = chart_info
        return new_state

    # ──────────────────────────────────────────
    # 핵심 추론 로직
    # ──────────────────────────────────────────

    def _infer(self, question: str, df: pd.DataFrame) -> Dict[str, Any]:
        q = question.lower()

        CHART_KEYWORDS = {
            "bar":   ["막대", "bar", "바차트", "수직", "수평", "비교"],
            "line":  ["꺾은선", "추이", "트렌드", "line", "선그래프", "변화", "증감"],
            "table": ["표", "테이블", "table", "목록", "리스트"],
        }
        GENERAL_KW = ["그래프", "차트", "chart", "graph", "시각화", "보여줘", "그려줘"]

        # 1. 특정 차트 타입 키워드 감지
        detected_type: Optional[str] = None
        for ctype, kws in CHART_KEYWORDS.items():
            if any(kw in q for kw in kws):
                detected_type = ctype
                break

        general_requested = any(kw in q for kw in GENERAL_KW)

        if detected_type is None and not general_requested:
            return {"type": "none"}

        if df.empty or len(df.columns) < 1:
            return {"type": "none"}

        # 2. 컬럼 분류
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

        datetime_cols = [
            c for c in df.columns
            if pd.api.types.is_datetime64_any_dtype(df[c])
            or self._DT_PATTERN.search(c)
            or any(kw in c for kw in self._DT_KOREAN_AGGS)
            or any(kw in c for kw in self._DT_HANGUL)
        ]

        # 세분화된 날짜 컬럼 우선 정렬 (month > day > date > year)
        datetime_cols_sorted = sorted(
            datetime_cols,
            key=lambda c: next(
                (i for i, kw in enumerate(self._PRIORITY)
                 if re.search(rf'(?<![a-z]){re.escape(kw)}(?![a-z])', c, re.IGNORECASE)),
                len(self._PRIORITY),
            ),
        )

        # 3. x축 결정: 날짜 > 문자형 > 첫 번째 컬럼
        if datetime_cols_sorted:
            x_col = datetime_cols_sorted[0]
        elif non_numeric_cols:
            x_col = non_numeric_cols[0]
        else:
            x_col = df.columns[0]

        # 4. y축 후보: 숫자형 중 x축·날짜 컬럼 제외
        y_candidates = [c for c in numeric_cols if c != x_col and c not in datetime_cols]
        if not y_candidates:
            y_candidates = [c for c in numeric_cols if c != x_col]
        if not y_candidates and numeric_cols:
            y_candidates = [numeric_cols[0]]
        if not y_candidates:
            return {"type": "none"}

        y_col: Any = y_candidates[0] if len(y_candidates) == 1 else y_candidates

        # 5. 차트 타입 자동 결정 (일반 요청인 경우)
        if detected_type is None:
            trend_kws = ["추이", "변화", "증감", "트렌드"]
            time_kws = ["월별", "분기별", "연도별", "일별"] + trend_kws
            if any(kw in q for kw in trend_kws):
                detected_type = "line"
            elif any(kw in q for kw in time_kws) or datetime_cols:
                detected_type = "bar"
            elif len(df) <= 5:
                detected_type = "table"
            else:
                detected_type = "bar"

        # 6. Dual Y-Axis 분석 (y컬럼이 복수이고 스케일 차이 > 10배)
        use_secondary = False
        y_axes: Dict[str, str] = {}

        if isinstance(y_col, list) and len(y_col) > 1 and detected_type in ("bar", "line"):
            # 날짜/x컬럼이 y_col에 섞인 경우 제거
            y_col = [c for c in y_col if c != x_col and c not in datetime_cols]
            if len(y_col) == 1:
                y_col = y_col[0]

            if isinstance(y_col, list) and len(y_col) > 1:
                try:
                    scales: Dict[str, float] = {}
                    for col in y_col:
                        vals = df[col].dropna()
                        if len(vals) > 0:
                            scales[col] = float(vals.max()) - float(vals.min())

                    if len(scales) >= 2:
                        max_r = max(scales.values())
                        min_r = min(scales.values())
                        if min_r > 0 and max_r / min_r > 10:
                            use_secondary = True
                            sorted_cols = sorted(scales.items(), key=lambda x: x[1], reverse=True)
                            for i, (col, _) in enumerate(sorted_cols):
                                y_axes[col] = "primary" if i == 0 else "secondary"
                except Exception as e:
                    logger.warning(f"Dual Y-Axis 분석 실패: {e}")

        # 7. DataFrame → Recharts data 직렬화 (NaN → None for JSON)
        data_records = df.where(pd.notnull(df), None).to_dict("records")
        data_keys = [y_col] if isinstance(y_col, str) else list(y_col)

        axis_info = " (Dual Axis)" if use_secondary else ""
        logger.info(
            f"📊 차트 결정: type={detected_type}{axis_info}, "
            f"xKey={x_col}, dataKeys={data_keys}, rows={len(df)}"
        )

        return {
            "type": detected_type,
            "title": question if len(question) <= 80 else question[:77] + "...",
            "xKey": x_col,
            "dataKeys": data_keys,
            "useSecondaryAxis": use_secondary,
            "yAxes": y_axes,
            "data": data_records,
        }
