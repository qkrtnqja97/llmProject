"""
비즈니스 용어 정의
- term + desc 결합 텍스트가 임베딩 대상(document)
- term, desc는 메타데이터로 저장
"""

BIZTERM_DATA = [
    {"term": "재고회전율", "desc": "판매량/현재재고. sales_orders.sale_quantity 합계 / current_products.current_quantity. 높을수록 잘 팔림"},
    {"term": "마진율", "desc": "(std_selling_price - std_unit_cost)/std_unit_cost*100. products 테이블 사용"},
    {"term": "데드스톡", "desc": "6개월 이상 판매 없는 재고. current_products LEFT JOIN sales_orders 후 매출 없는 품목"},
    {"term": "매출총이익", "desc": "actual_selling_price - std_unit_cost. sales_orders와 products 조인 후 계산"},
    {"term": "ABC분석", "desc": "매출 기여도로 품목 분류. A=누적80%, B=누적95%, C=나머지. 윈도우함수 SUM OVER 사용"},
    {"term": "매입단가", "desc": "actual_unit_cost(실제) 또는 std_unit_cost(표준). purchase_orders 또는 products 테이블"},
    {"term": "판매단가", "desc": "actual_selling_price(실제) 또는 std_selling_price(표준). sales_orders 또는 products"},
    {"term": "안전재고", "desc": "수요 변동 대비 최소 보유 재고. 평균 일판매량 * 조달기간으로 산출"},
    {"term": "발주점", "desc": "재주문 필요 재고 수준. 현재고가 이하면 발주 필요"},
    {"term": "리드타임", "desc": "발주~입고 소요일. purchase_orders.purchase_date 기준 분석"},
    {"term": "수익성", "desc": "매출총이익 = 판매금액 - 매입원가. actual_selling_price * qty - std_unit_cost * qty"},
    {"term": "매출액", "desc": "sale_quantity * actual_selling_price 합계. sales_orders 테이블에서 집계"},
    {"term": "매입액", "desc": "purchase_quantity * actual_unit_cost 합계. purchase_orders 테이블에서 집계"},
    {"term": "ASP (평균판매단가)", "desc": "총 매출액을 총 판매수량으로 나눈 값. SUM(sale_quantity * actual_selling_price) / SUM(sale_quantity)"},
    {"term": "YoY (전년동기대비)", "desc": "작년 동일 기간과 올해 기간의 수치를 비교. EXTRACT(YEAR FROM date)를 활용해 각각 집계 후 비교"},
    {"term":"윈터-스냅 (Winter-Snap)","desc":"2022-12-31 기준의 시스템 초기 재고 스냅샷 데이터로 모든 재고 흐름의 절대적 기준점. initial_inventory / stock_date"},
    {"term":"수금-웨이브 (Wed-Fri Wave)","desc":"매주 수요일·금요일에 발생하는 정기 출고 물류 흐름이며 '웨이브에 태우다'는 출고 예약을 의미. sales_orders / sale_date"},
    {"term":"다크-텐 (Dark-10)","desc":"전체 품목 중 입출고가 전혀 없는 10%의 악성 재고군으로 창고 점유율만 차지하는 관리 대상 품목. current_products / 비즈니스 제약 4번"},
    {"term":"보름-배치 (Fortnight Batch)","desc":"매월 1일과 15일에 집중 입고되는 대량 발주 건으로 정기 발주를 통한 원가 절감 매입 단계. purchase_orders / purchase_date"},
    {"term":"고스트-피엔 (Ghost PN)","desc":"마스터에는 등록되어 있으나 실제 거래 이력이 없는 신규·적체 품목으로 데이터만 존재하는 상태. products / part_number"},
    {"term":"델타-체크 (Delta Check)","desc":"실시간 재고량과 (기초+입고-출고) 계산값 일치 여부를 검증하는 데이터 무결성 감사 행위. current_products / initial_inventory"},
    {"term":"골든-마진 (Golden Margin)","desc":"고시가(표준가)보다 실제 판매가가 높게 책정되어 수익이 극대화된 우수 계약 상태. products / sales_orders"},
    {"term":"유니크-락 (Unique Lock)","desc":"제조사명 중복 등록 제약으로 신규 업체 등록이 차단된 상태로 기존 업체 확인이 필요한 상황. manufacturers / UNIQUE constraint"},
    {"term":"제로-베이스 위반 (Zero-Base Violation)","desc":"판매 날짜가 최초 구매 날짜보다 앞서는 논리적 날짜 오류로 데이터 입력 순서가 꼬인 상태. 비즈니스 제약 3번"},
    {"term":"유닛-태깅 (Unit Tagging)","desc":"표준 매입 원가를 확정해 분기별 예산 수립 기준을 설정하는 행위로 원가 변동 방어 목적. products / std_unit_cost"}
]
