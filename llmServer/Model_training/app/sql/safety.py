"""
[SQL] Safety Guard

 역할
- 실행 전에 SQL이 안전한 SELECT/WITH 계열인지 최소 검증한다.
- 코멘트 제거, 멀티 스테이트먼트 차단, 위험 키워드/함수 차단을 수행한다.
"""

from __future__ import annotations

import re

# 코멘트 제거 정규식
RE_LINE_COMMENT = re.compile(r"--.*?$", re.MULTILINE)
RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

# 위험 키워드(최소 방어)
FORBIDDEN = re.compile(
    r"\b("
    r"drop|delete|truncate|alter|update|insert|create|grant|revoke|"
    r"copy|call|do|execute|vacuum|analyze|"
    r"listen|notify"
    r")\b",
    re.IGNORECASE,
)

# 위험 함수(DoS 방지)
FORBIDDEN_FUNC = re.compile(r"\bpg_sleep\s*\(", re.IGNORECASE)


def _strip_comments(sql: str) -> str:
    """
    SQL에서 라인/블록 코멘트를 제거한다.

    Args:
        sql: 원본 SQL

    Returns:
        코멘트 제거된 SQL
    """
    s = RE_BLOCK_COMMENT.sub("", sql)
    s = RE_LINE_COMMENT.sub("", s)
    return s


def _assert_single_statement(sql: str) -> None:
    """
    멀티 스테이트먼트(;)를 차단한다.
    - 끝의 단일 ';'는 허용(제거 후 검사)
    - 중간 ';' 존재 시 차단

    Args:
        sql: 코멘트 제거 후 SQL

    Raises:
        ValueError: 멀티 스테이트먼트 의심 시
    """
    s = sql.strip()
    if not s:
        raise ValueError("빈 SQL은 실행할 수 없습니다.")

    if s.endswith(";"):
        s = s[:-1].strip()

    if ";" in s:
        raise ValueError("멀티 스테이트먼트(;)가 감지되어 실행을 차단했습니다.")


def assert_safe_select(sql: str) -> None:
    """
    SQL이 안전한 SELECT/WITH 계열인지 최소 검증한다.

    Args:
        sql: 실행할 SQL 문자열

    Raises:
        ValueError: 위험한 키워드/패턴이 있거나 SELECT/WITH로 시작하지 않으면 예외
    """
    raw = (sql or "").strip()
    if not raw:
        raise ValueError("빈 SQL은 실행할 수 없습니다.")

    s = _strip_comments(raw).strip()

    if not (s.lower().startswith("select") or s.lower().startswith("with")):
        raise ValueError("SELECT/WITH로 시작하지 않는 SQL은 허용하지 않습니다.")

    _assert_single_statement(s)

    if FORBIDDEN.search(s):
        raise ValueError("위험 SQL 키워드가 포함되어 있어 실행을 차단했습니다.")

    if FORBIDDEN_FUNC.search(s):
        raise ValueError("위험 함수 호출이 감지되어 실행을 차단했습니다.")
