#model_training/create_data/slot_rules.py
"""
[SLOT RULES] SQL 템플릿화(Template) + 슬롯(slot) 추출 규칙 모듈

📌 역할
- DB에 저장된 "완성 SQL(final_sql)"에서 재사용 가능한 "sql_template"을 만들고,
  동시에 템플릿에 들어갈 변수 값(=slots)을 추출한다.
- 목적: RAG에서 SQL을 '생성'하지 않고 '템플릿+slot 조립'으로 재사용하기 위함.

✅ 입력 예시(final_sql)
- ... WHERE part_number='P001' AND strftime('%Y', sale_date)='2024';

✅ 출력 예시
- sql_template:
  ... WHERE part_number={{part_number}} AND strftime('%Y', sale_date)={{year}};
- slots:
  {"part_number": "P001", "year": "2024"}

📦 사용 라이브러리 (표준 라이브러리만 사용)
- re: 정규식 기반 슬롯 추출/치환
- typing: 타입 힌트
"""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple


# -----------------------------
# 정규식 패턴들 (slot 후보)
# -----------------------------
# [PART] part_number='P001'
RE_PART = re.compile(r"part_number\s*=\s*'([^']+)'", re.IGNORECASE)

# [YEAR/MONTH] strftime('%Y', sale_date)='2024' 형태 (SQLite 스타일)
RE_YEAR_SALE = re.compile(
    r"strftime\('%Y'\s*,\s*sale_date\)\s*=\s*'(\d{4})'",
    re.IGNORECASE,
)
RE_MONTH_SALE = re.compile(
    r"strftime\('%m'\s*,\s*sale_date\)\s*=\s*'(\d{2})'",
    re.IGNORECASE,
)

RE_YEAR_PURCHASE = re.compile(
    r"strftime\('%Y'\s*,\s*purchase_date\)\s*=\s*'(\d{4})'",
    re.IGNORECASE,
)
RE_MONTH_PURCHASE = re.compile(
    r"strftime\('%m'\s*,\s*purchase_date\)\s*=\s*'(\d{2})'",
    re.IGNORECASE,
)

# [VENDOR/MFR] vendor_id=3 / manufacturer_id=12 형태
RE_VENDOR_ID = re.compile(r"\bvendor_id\s*=\s*(\d+)\b", re.IGNORECASE)
RE_MANUFACTURER_ID = re.compile(r"\bmanufacturer_id\s*=\s*(\d+)\b", re.IGNORECASE)


def normalize_sql_whitespace(sql: str) -> str:
    """
    SQL 문자열의 공백/개행을 정규화하는 함수

    Args:
        sql: 원본 SQL 문자열

    Returns:
        str: 공백이 정리된 SQL 문자열
    """
    return re.sub(r"\s+", " ", sql).strip()


def patternize_sql(final_sql: str) -> Tuple[str, Dict[str, Any]]:
    """
    완성 SQL(final_sql)을 템플릿(sql_template)과 슬롯(slots)으로 분리하는 함수

    처리 방식:
    1) 정규식으로 slot 값을 찾는다.
    2) 찾은 값을 {{slot_name}} placeholder로 치환한다.
    3) 템플릿과 슬롯 dict를 반환한다.

    Args:
        final_sql: 완성 SQL 문자열

    Returns:
        (sql_template, slots)
        - sql_template: placeholder 포함 템플릿 SQL
        - slots: 추출된 slot 값 dict

    Notes:
        - 현재는 ERP에서 자주 나오는 slot(연/월/파트/벤더/제조사) 위주.
        - 추후 top_n, date_from/to 등 확장 가능.
    """
    if not final_sql or not str(final_sql).strip():
        return "", {}

    t = str(final_sql)
    slots: Dict[str, Any] = {}

    # 1) part_number
    m = RE_PART.search(t)
    if m:
        slots["part_number"] = m.group(1)
        t = RE_PART.sub("part_number={{part_number}}", t)

    # 2) vendor_id (모든 vendor_id=숫자 를 동일 placeholder로 치환)
    vids = RE_VENDOR_ID.findall(t)
    if vids:
        slots["vendor_id"] = int(vids[0])
        t = RE_VENDOR_ID.sub("vendor_id={{vendor_id}}", t)

    # 3) manufacturer_id
    mids = RE_MANUFACTURER_ID.findall(t)
    if mids:
        slots["manufacturer_id"] = int(mids[0])
        t = RE_MANUFACTURER_ID.sub("manufacturer_id={{manufacturer_id}}", t)

    # 4) year/month for sale_date
    ys = RE_YEAR_SALE.findall(t)
    if ys:
        slots["year"] = ys[0]
        t = RE_YEAR_SALE.sub("strftime('%Y', sale_date)={{year}}", t)

    ms = RE_MONTH_SALE.findall(t)
    if ms:
        slots["month"] = ms[0]
        t = RE_MONTH_SALE.sub("strftime('%m', sale_date)={{month}}", t)

    # 5) year/month for purchase_date
    yp = RE_YEAR_PURCHASE.findall(t)
    if yp and "year" not in slots:
        slots["year"] = yp[0]
    if yp:
        t = RE_YEAR_PURCHASE.sub("strftime('%Y', purchase_date)={{year}}", t)

    mp = RE_MONTH_PURCHASE.findall(t)
    if mp and "month" not in slots:
        slots["month"] = mp[0]
    if mp:
        t = RE_MONTH_PURCHASE.sub("strftime('%m', purchase_date)={{month}}", t)

    # 6) whitespace normalize
    sql_template = normalize_sql_whitespace(t)

    return sql_template, slots


if __name__ == "__main__":
    # ✅ 간단 셀프 테스트 (로컬에서만)
    sample = """
    SELECT SUM(sale_quantity*actual_selling_price)
    FROM sales_orders
    WHERE part_number='P001'
      AND vendor_id=3
      AND strftime('%Y', sale_date)='2024'
      AND strftime('%m', sale_date)='03';
    """
    tpl, slots = patternize_sql(sample)
    print("TEMPLATE:", tpl)
    print("SLOTS:", slots)