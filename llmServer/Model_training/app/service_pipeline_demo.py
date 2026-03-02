"""
[DEMO] End-to-End Pipeline Demo (RAG → slot → render → Postgres)

📌 역할
- 질문 1개로 end-to-end 파이프라인을 실행해, "검색/슬롯/선택/렌더링/안전/실행"이
  DB 변경 이후에도 정상인지 빠르게 검증한다.

📌 기능 맵(번호 체계: 상위-하위)
1) 환경설정 로딩
2) DB에서 실존 part_number 자동 선택
3) 데모 질문 생성(테스트 케이스 변경 포인트)

4) 슬롯/의미 추출 레이어
   4-1) 기본 슬롯 추출(year/month/part_number/intent)
   4-2) intent fallback(슬롯에 intent 없을 때 텍스트 기반 추정)
   4-3) metric 추정(qty=판매량/수량 vs amount=매출/금액)

5) 미지원 용어 가드(헛SQL 방지)
   5-1) unsupported_terms 감지 시 즉시 중단

7) RAG 검색 질의 보강
   7-1) intent 기반 보강(SALES_HINTS/PURCHASE_HINTS)
   7-2) metric 기반 보강(qty/amount 토큰 추가)

8) 템플릿 선택 로직
   8-1) slots_schema 없는 템플릿 제거(하드코딩/레거시 배제)
   8-2) 슬롯 정합성 필터(required slots 충족)
   8-3) 도메인 필터(sales vs purchase)
   8-4) metric 우선순위(qty 템플릿 vs amount 템플릿)

9) SQL 렌더링 → Safety 검증 → DB 실행 및 출력
"""

from __future__ import annotations
import time

from typing import Any, Dict, List, Optional

from app.config import load_settings
from app.rag.search import search_templates
from app.slots.extractor_rules import extract_slots
from app.sql.template_renderer import render_sql
from app.sql.safety import assert_safe_select
from app.runtime.query_runner_postgres import run_query
from app.runtime.request_logger_postgres import log_request
from app.runtime.gold_publisher_postgres import publish_gold_from_request_id


# ------------------------------------------------------------
# [7-1] intent 기반 검색 보강 / [8-3] 도메인 판정에 쓰는 힌트 토큰
# ------------------------------------------------------------
SALES_HINTS = ("sales_orders", "sale_date", "sale_quantity", "actual_selling_price")
PURCHASE_HINTS = ("purchase_orders", "purchase_date", "purchase_quantity", "actual_unit_cost")


def _augment_query_for_intent(question: str, intent: Optional[str]) -> str:
    """
    [7-1] RAG 검색 질의를 intent 기반으로 보강한다.

    Args:
        question: 원 질문
        intent: 'sales' | 'purchase' | None

    Returns:
        보강된 검색 질의 문자열
    """
    q = (question or "").strip()

    if intent == "sales":
        return q + " " + " ".join(SALES_HINTS)

    if intent == "purchase":
        return q + " " + " ".join(PURCHASE_HINTS)

    return q


def _augment_query_for_metric(retrieval_query: str, metric: Optional[str], intent: Optional[str]) -> str:
    """
    [7-2] metric 기반으로 검색 질의를 추가 보강한다.

    설계:
    - metric은 sales 질문에서 특히 중요(판매량 vs 매출금액).
    - purchase도 확장 가능하지만 MVP에서는 sales 중심으로 힌트를 준다.

    Args:
        retrieval_query: 이미 intent 기반 보강이 끝난 질의 문자열
        metric: 'qty' | 'amount' | None
        intent: 'sales' | 'purchase' | None

    Returns:
        metric 토큰이 추가된 retrieval_query
    """
    q = retrieval_query

    # 현재는 sales 위주로만 강화 (필요시 purchase도 확장)
    if intent != "sales":
        return q

    if metric == "qty":
        # 판매량/수량 계열 토큰(템플릿 매칭 유도)
        q += " sum(sale_quantity) total_qty 판매수량 판매량 수량"
    elif metric == "amount":
        # 매출/금액 계열 토큰(템플릿 매칭 유도)
        q += " sum(sale_quantity*actual_selling_price) total_amount sales_amount 매출금액 매출 금액"
    return q


def _is_sales_template(sql_template: str) -> bool:
    """
    [8-3] 템플릿이 sales 도메인인지 휴리스틱으로 판정한다.
    """
    tpl = (sql_template or "").lower()
    return any(h in tpl for h in SALES_HINTS)


def _is_purchase_template(sql_template: str) -> bool:
    """
    [8-3] 템플릿이 purchase 도메인인지 휴리스틱으로 판정한다.
    """
    tpl = (sql_template or "").lower()
    return any(h in tpl for h in PURCHASE_HINTS)


def _has_required_slots(hit: Dict[str, Any], slots: Dict[str, Any]) -> bool:
    """
    [8-2] 템플릿이 요구하는 slots_schema를 실제 추출된 slots가 모두 만족하는지 검사한다.

    Args:
        hit: RAG 검색 결과 1개 (sql_template, slots_schema 등 포함)
        slots: 질문에서 추출된 슬롯 dict

    Returns:
        필수 슬롯을 만족하면 True
    """
    schema = (hit.get("slots_schema") or "").strip()
    if not schema:
        # slots_schema가 없으면(레거시) 여기서는 True 처리하지만,
        # [8-1]에서 slots_schema 없는 템플릿은 전체 제외한다.
        return True

    required = [s.strip() for s in schema.split(",") if s.strip()]
    return all(k in slots and slots.get(k) not in (None, "") for k in required)


def _is_qty_template(sql_template: str) -> bool:
    """
    [8-4] qty(판매량/수량) 템플릿을 휴리스틱으로 판정한다.

    기준(MVP):
    - SUM(sale_quantity) 포함이면 qty로 본다.
    """
    tpl = (sql_template or "").lower().replace(" ", "")
    return "sum(sale_quantity)" in tpl and "sale_quantity*actual_selling_price" not in tpl


def _is_amount_template(sql_template: str) -> bool:
    """
    [8-4] amount(매출/금액) 템플릿을 휴리스틱으로 판정한다.

    기준(MVP):
    - sale_quantity*actual_selling_price 포함이면 amount로 본다.
    """
    tpl = (sql_template or "").lower().replace(" ", "")
    return "sale_quantity*actual_selling_price" in tpl


def _pick_existing_part_number(year: int = 2024) -> Optional[str]:
    """
    [2] 현재 DB에서 실제로 존재하는 part_number를 하나 선택한다.

    Args:
        year: 기준 연도

    Returns:
        part_number 또는 None
    """
    sql = f"""
        SELECT part_number
        FROM sales_orders
        WHERE EXTRACT(YEAR FROM sale_date) = {int(year)}
        GROUP BY part_number
        ORDER BY COUNT(*) DESC
        LIMIT 1;
    """
    _, rows = run_query(sql, row_limit=10)
    if not rows:
        return None
    return rows[0].get("part_number")


def _choose_best_hit(
    hits: List[Dict[str, Any]],
    intent: Optional[str],
    slots: Dict[str, Any],
    metric: Optional[str],
) -> Dict[str, Any]:
    """
    [8] hits 중에서 최적 템플릿을 선택한다.

    적용 순서(중요)
    8-1) slots_schema 없는 템플릿 제거
    8-2) 슬롯 정합성 필터(required slots 충족)
    8-3) 도메인 필터(sales/purchase)
    8-4) metric 우선순위(qty/amount)
    fallback: 그래도 못 고르면 hits[0]

    Args:
        hits: search_templates 결과 리스트
        intent: 'sales' | 'purchase' | None
        slots: 질문에서 추출된 슬롯(dict)
        metric: 'qty' | 'amount' | None

    Returns:
        선택된 hit(dict)

    Raises:
        ValueError: hits가 비었거나, 유효한 템플릿이 없을 때
    """
    if not hits:
        raise ValueError("hits가 비어있습니다.")

    # -------------------------
    # [8-1] slots_schema 없는 템플릿 제외 (하드코딩/레거시 배제)
    # -------------------------
    hits = [h for h in hits if (h.get("slots_schema") or "").strip()]
    if not hits:
        raise ValueError("유효한 slots_schema를 가진 템플릿이 없습니다. 템플릿 라이브러리 정제 필요.")

    # -------------------------
    # [8-2] 필수 슬롯 정합성 필터
    # -------------------------
    filtered = [h for h in hits if _has_required_slots(h, slots)]
    if filtered:
        hits = filtered

    # -------------------------
    # [8-3] 도메인 필터
    # -------------------------
    if intent == "sales":
        domain_hits = [h for h in hits if _is_sales_template(h.get("sql_template") or "")]
        if domain_hits:
            hits = domain_hits

        # -------------------------
        # [8-4] metric 우선순위 (sales에서만 적용)
        # -------------------------
        if metric == "qty":
            # ✅ qty 후보: SUM(sale_quantity)가 들어있는 템플릿이면 전부 후보로 인정
            qty_hits = [
                h for h in hits 
                if "sum(sale_quantity)"in (h.get("sql_template") or "").lower().replace(" ", "")]
            if qty_hits:
                # ✅ month 같은 슬롯을 더 많이 쓰는 템플릿 우선
                qty_hits.sort(key=lambda h: len((h.get("slots_schema") or "").split(",")), reverse=True)
                return qty_hits[0]
        elif metric == "amount":
            amt_hits = [h for h in hits if _is_amount_template(h.get("sql_template") or "")]
            if amt_hits:
                return amt_hits[0]

        return hits[0]

    if intent == "purchase":
        domain_hits = [h for h in hits if _is_purchase_template(h.get("sql_template") or "")]
        if domain_hits:
            hits = domain_hits
        return hits[0]

    # intent가 None이면 그냥 1등
    return hits[0]


def main() -> None:
    """
    [MAIN] 데모 실행 엔트리
    - 성공/실패와 무관하게 request_logs에 1건 저장한다.
    """
    # -------------------------
    # [LOG] 요청 로그용 변수 초기화 (성공/실패 공통)
    # -------------------------
    question = ""
    retrieval_query = None
    intent = None
    metric = None
    slots: Dict[str, Any] = {}
    best = None
    final_sql = None

    error_message = None
    execution_success = False
    user_satisfaction = None
    row_count = 0
    preview = []
    elapsed_ms = None
    error_type = "OK"
    try: 

        # -------------------------
        # [1] 환경설정 로딩
        # -------------------------
        settings = load_settings()

        # -------------------------
        # [2] DB에서 실존 part_number 자동 선택
        # -------------------------
        year = 2024
        pn = _pick_existing_part_number(year=year)
        if not pn:
            print("❌ sales_orders에서 테스트용 part_number를 찾지 못했습니다. (데이터/연도 확인 필요)")
            return

        # -------------------------
        # [3] 데모 질문 생성 (여기만 바꾸면 테스트 케이스 교체)
        # -------------------------
        default_q = f"{year}년 3월 {pn} 판매량은?"
        question = input(f"질문을 입력하세요(엔터=기본:{default_q}): ").strip()
        if not question:
            question = default_q
        
        # -------------------------
        # [4-1] 기본 슬롯 추출
        # -------------------------
        slots = extract_slots(question)

        q_lower = question.lower()
        unsupported_terms = ["quantity"]  # 필요 시 확장
        for t in unsupported_terms:
            if t in q_lower:
                raise ValueError(f" 미지원 용어 감지: '{t}'. 스키마/템플릿에 정의된 컬럼명으로 질문해야 합니다.")


        # -------------------------
        # [4-2] intent fallback (슬롯에 intent 없을 때 텍스트 기반 추정)
        # -------------------------
        intent = slots.get("intent")
        if not intent:
            q = question.lower()
            if "매출" in q or "판매" in q:
                intent = "sales"
            elif "매입" in q or "구매" in q:
                intent = "purchase"

        # -------------------------
        # [4-3] metric 추정 (qty vs amount)
        # -------------------------
        metric: Optional[str] = None
        q = question.lower()
        if "판매량" in q or "수량" in q:
            metric = "qty"
        elif "매출" in q or "금액" in q:
            metric = "amount"

        # -------------------------
        # [7-1] intent 기반 검색 질의 보강
        # -------------------------
        retrieval_query = _augment_query_for_intent(question, intent)

        # -------------------------
        # [7-2] metric 기반 검색 질의 추가 보강
        # -------------------------
        retrieval_query = _augment_query_for_metric(retrieval_query, metric, intent)

        # RAG 검색
        hits = search_templates(settings, retrieval_query)
        
        print("Q:", question)
        print("retrieval_query:", retrieval_query)
        print("HITS:", len(hits))
        if not hits:
            raise ValueError("템플릿 검색 실패")

        # -------------------------
        # [8] 템플릿 선택
        # -------------------------
        best = _choose_best_hit(hits, intent, slots, metric)

        sql_template = best["sql_template"]
        slots_schema = best.get("slots_schema", "")

        print("slots_schema:", slots_schema)
        print("slots:", slots)
        print("metric:", metric)
        print("intent:", intent)
        print("chosen_pattern_id:", best.get("pattern_id"))
        print("chosen_distance:", best.get("distance"))

        # -------------------------
        # [9] SQL 렌더링 → Safety → DB 실행
        # -------------------------
        print("sql_template:", sql_template)
        final_sql = render_sql(sql_template, slots)
        print("final_sql:", repr(final_sql))

        assert_safe_select(final_sql)

        print("\n[FINAL SQL]\n", final_sql)

        t0 = time.time()
        row_count, preview = run_query(final_sql, row_limit=200)
        elapsed_ms = int((time.time() - t0) * 1000)

        execution_success = True
        raw = input("사용자 만족도를 입력하세요(1: 매우 만족, 0: 보통, -1: 매우 불만족): ").strip()
        if raw == "":
            user_satisfaction = 0
        else:
            v = int(raw)
            if v in (-1, 0, 1):
                user_satisfaction = v
            else:
                user_satisfaction = 0

        print("\n[RESULT] rows:", row_count)
        print("preview:", preview[:3])
        print("question_repr:", repr(question))
        
        
    except Exception as e:
        error_message = str(e)
        execution_success = False
        print("❌ ERROR:", error_message)

        msg = (error_message or "").lower()

        if "미지원 용어 감지" in error_message:
            error_type = "UNSUPPORTED_TERM"
        elif "위험 sql" in msg or "멀티 스테이트먼트" in msg:
            error_type = "SAFETY_BLOCK"
        elif "템플릿 검색 실패" in error_message:
            error_type = "TEMPLATE_NOT_FOUND"
        elif final_sql is not None:
            error_type = "DB_ERROR"
        else:
            error_type = "UNKNOWN"

        # DEBUG 모드일 때만 traceback 출력
        debug = bool(getattr(settings, "debug", False)) if "settings" in locals() else False
        if debug:
            import traceback
            traceback.print_exc()  

    finally:
        request_id = None

        # 1) request_logs 저장
        try:
            if execution_success and isinstance(best, dict) and best.get("pattern_id"):
                from app.runtime.request_logger_postgres import increment_usage_count
                increment_usage_count(best.get("pattern_id"))

            request_id = log_request(
                question=question,
                refined_question=retrieval_query,
                selected_pattern_id=best.get("pattern_id") if isinstance(best, dict) else None,
                slots_json=slots,
                final_sql=final_sql,
                execution_success=execution_success,
                execution_time_ms=elapsed_ms,
                row_count=row_count,
                error_type=error_type,
                error_message=error_message,
                user_id=None,
                user_satisfaction=user_satisfaction,
                entity_corrections={},
            )
            print("✅ request_logs saved:", request_id)

        except Exception as e:
            print("❌ request_logs 저장 실패:", e)

        # 2) gold publish (request_id가 있을 때만)
        if request_id and execution_success and user_satisfaction == 1:
            try:
                published, reason = publish_gold_from_request_id(request_id)
                print(f"✅ gold publish: {published} ({reason})")
            except Exception as e:
                print("❌ gold publish 실패:", e)


if __name__ == "__main__":
    main()