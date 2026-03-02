"""
[SLOTS] Rule-based Slot Extractor

📌 역할
- 사용자 질문(text)에서 SQL 템플릿에 필요한 slot 값을 추출한다.
- 예: "2024년 EN2210-BG1의 총 매출" -> {"year":"2024","part_number":"EN2210-BG1","intent":"sales"}

✅ 추출 대상(MVP)
- year: 4자리 연도(20xx년)
- month: 1~12월 → 2자리(01~12)로 정규화
- part_number: 하이픈 포함 부품코드 또는 6자 이상 토큰
- vendor_id: "벤더 3" 같은 숫자
- manufacturer_id: "제조사 12" 같은 숫자
- intent: 판매/매출(sales) vs 구매/매입(purchase) 키워드

📦 사용 라이브러리
- re: 정규식 추출
- typing: 타입 힌트
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


# -----------------------------
# 정규식 패턴
# -----------------------------
RE_YEAR = re.compile(r"(20\d{2})\s*년")
RE_MONTH = re.compile(r"(\d{1,2})\s*월")

# ✅ 다양한 유니코드 하이픈을 모두 허용
HYPHENS = r"\-\u2010\u2011\u2012\u2013\u2014\u2212\uFE63\uFF0D"

# part_number 패턴:
# 1) 하이픈 포함 토큰: EN2210-BG1, A3P1000-2FG484, 98DX-BHA1 ...
# 2) 하이픈 없는 긴 토큰: ADS62C15IRGCT ...
RE_PART = re.compile(
    rf"(?<![A-Z0-9#])([A-Z0-9][A-Z0-9#]*(?:[{HYPHENS}][A-Z0-9#]+)+|[A-Z0-9]{{6,}})(?![A-Z0-9#])",
    re.IGNORECASE,
)

RE_VENDOR = re.compile(r"(?:벤더|vendor)\s*(\d+)", re.IGNORECASE)
RE_MFR = re.compile(r"(?:제조사|manufacturer)\s*(\d+)", re.IGNORECASE)


def _normalize_month_int(m: str) -> Optional[int]:
    """
    월 문자열을 1~12 범위의 int로 정규화

    ✅ 왜 int로 하냐?
    - 현재 Postgres 템플릿은 EXTRACT(MONTH FROM date)= {{month}} 형태가 많다.
    - EXTRACT(MONTH)은 정수(1~12)를 반환하므로 month slot도 int가 맞다.

    Args:
        m: '3' 또는 '03' 형태 문자열

    Returns:
        3 같은 int (범위 밖이면 None)
    """
    mm = int(m)
    if mm < 1 or mm > 12:
        return None
    return mm


def extract_intent(question: str) -> Optional[str]:
    """
    질문에서 의도(intent)를 간단히 추출

    Args:
        question: 사용자 질문

    Returns:
        'sales' | 'purchase' | None
    """
    q = (question or "").strip()
    if not q:
        return None

    sales_kw = ["매출", "판매", "sell", "sales"]
    purchase_kw = ["구매", "매입", "buy", "purchase", "procure"]

    if any(k in q for k in sales_kw):
        return "sales"
    if any(k in q for k in purchase_kw):
        return "purchase"
    return None


def extract_part_number(question: str) -> str:
    """
    질문에서 part_number를 추출 (가장 긴 매칭 우선)

    처리 전략:
    - RE_PART에 매칭되는 모든 토큰을 찾는다.
    - 그 중 가장 긴 문자열을 part_number로 선택한다.
      (예: EN2210 vs EN2210-BG1 → EN2210-BG1 선택)

    Args:
        question: 사용자 질문

    Returns:
        str: 추출된 part_number (없으면 "")
    """
    q = (question or "").strip()
    if not q:
        return ""

    # ✅ 유니코드 하이픈/마이너스 전부 일반 '-'로 정규화
    # - U+2010: ‐
    # - U+2012: ‒
    # - U+2013: –
    # - U+2014: —
    # - U+2212: −
    # - U+FE63: ﹣
    # - U+FF0D: －
    hyphens = {
        ord("‐"): "-", ord("-"): "-", ord("‒"): "-", ord("–"): "-",
        ord("—"): "-", ord("−"): "-", ord("﹣"): "-", ord("－"): "-",
        }
    q = q.translate(hyphens)
    q = q.upper()
    # ✅ search() 대신 finditer()로 전체 후보를 모은다.
    matches = [m.group(0) for m in RE_PART.finditer(q)]
    if not matches:
        return ""

    # ✅ 가장 긴 토큰 선택
    best = max(matches, key=len)
    return best.upper()


def extract_slots(question: str) -> Dict[str, Any]:
    """
    질문에서 SQL 템플릿 렌더링에 필요한 slot들을 한 번에 추출

    service_pipeline_demo.py가 요구하는 entrypoint:
    - extract_slots(question) -> dict

    Args:
        question: 사용자 질문

    Returns:
        dict:
          - year: int
          - month: int
          - part_number: str
          - vendor_id: int
          - manufacturer_id: int
          - intent: 'sales' | 'purchase'
    """
    q = (question or "").strip()
    slots: Dict[str, Any] = {}
    if not q:
        return slots

    # 1) intent
    intent = extract_intent(q)
    if intent:
        slots["intent"] = intent

    # 2) part_number
    part_number = extract_part_number(q)
    if part_number:
        slots["part_number"] = part_number

    # 3) year
    y = RE_YEAR.search(q)
    if y:
        slots["year"] = int(y.group(1))

    # 4) month
    mo = RE_MONTH.search(q)
    if mo:
        month_int = _normalize_month_int(mo.group(1))
        if month_int is not None:
            slots["month"] = month_int

    # 5) vendor_id
    v = RE_VENDOR.search(q)
    if v:
        slots["vendor_id"] = int(v.group(1))

    # 6) manufacturer_id
    m = RE_MFR.search(q)
    if m:
        slots["manufacturer_id"] = int(m.group(1))

    return slots