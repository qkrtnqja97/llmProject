#model_training/app/sql/template_renderer.py
"""
[SQL] Template Renderer

📌 역할
- RAG에서 가져온 sql_template에 slots 값을 채워 최종 SQL(final_sql)을 만든다.
- 템플릿 형식: {{slot_name}}
- 문자열 slot은 SQL 문법을 위해 기본적으로 따옴표로 감싼다.

📦 사용 라이브러리
- re: placeholder 치환
- typing: 타입 힌트
"""

from __future__ import annotations

import re
from typing import Any, Dict


# {{year}}, {{part_number}} 같은 placeholder 탐지
RE_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def _to_sql_literal(value: Any) -> str:
    """
    Python 값을 SQL literal로 변환하는 함수

    정책(MVP):
    - int/float: 그대로 반환
    - 숫자 문자열("2024"): 그대로 반환 (따옴표 없이)
    - 그 외 문자열: 작은따옴표로 감싸고 내부 '는 ''로 escape

    Args:
        value: slot 값

    Returns:
        str: SQL에 삽입 가능한 literal 문자열
    """
    # 숫자 타입은 그대로
    if isinstance(value, (int, float)):
        return str(value)

    s = str(value).strip()

    # year/month 같은 숫자 문자열이면 그대로
    if s.isdigit():
        return s

    # 문자열은 quoting + escape
    s = s.replace("'", "''")
    return f"'{s}'"


def render_sql(sql_template: str, slots: Dict[str, Any]) -> str:
    """
    sql_template에 slots를 채워 final SQL을 생성

    Args:
        sql_template: {{year}}, {{part_number}} 같은 placeholder가 포함된 템플릿
        slots: {"year":"2024","part_number":"EN2210-BG1"} 같은 dict

    Returns:
        str: 치환된 SQL(final_sql)
    """
    if not sql_template or not str(sql_template).strip():
        raise ValueError("sql_template이 비어있습니다.")

    tpl = str(sql_template)

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in slots:
            raise KeyError(f"필수 slot 누락: {key}")
        return _to_sql_literal(slots[key])

    final_sql = RE_PLACEHOLDER.sub(_replace, tpl)

    # ✅ 반드시 문자열 반환(여기서 None 반환되면 안 됨)
    return final_sql