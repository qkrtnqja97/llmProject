"""
테이블-컬럼 Rich 문장 (스키마 설명)
- doc 텍스트가 임베딩 대상(document)
- meta(table, columns, constraint)는 메타데이터로 저장
"""

TABLE_SCHEMA_DATA = [
    {
        "id": "products",
        "description": "제품(전자부품) 마스터 데이터. 제품의 고유 식별 번호는 'part_number'이며, 제품의 카테고리/유형은 'description' 컬럼에 저장되어 있음(예: IC, FET/TR, C_CHIP 등). 제품 식별 시 반드시 'part_number'와 'description'을 함께 고려해야 함.",
        "columns": "part_number, description, std_unit_cost, std_selling_price",
        "sql": "PK: part_number. 중요: 'part_number'는 제품의 고유 식별자(예: 80-CBR04C...)이며, 'description'은 제품의 카테고리(분류)임. 모든 분석 보고 시 제품은 'part_number'와 'description'을 함께 사용하여 지칭할 것."
    },
    {
        "id": "manufacturers",
        "description": "제품을 공급하는 제조사/공급처 마스터. '어느 업체가 공급했는지', '특정 제조사의 납품 이력' 등을 묻는 질문에 매핑됨. 업체명(name)은 고유하며 벤더/공급사 정보의 근원임.",
        "columns": "manufacturer_id, name",
        "sql": "PK: manufacturer_id. purchase_orders 테이블과 manufacturer_id로 조인하여 공급처별 매입금액/수량 집계. 업체명(name)을 통한 검색 및 조인 시 이 테이블을 거쳐야 함."
    },
    {
        "id": "vendors",
        "description": "제품을 구매해 가는 고객사/판매처 마스터. '고객사별 매출', '거래처 정보', '납품처 리스트'를 묻는 질문에 대응. 매출 분석 시 고객 식별의 기준임.",
        "columns": "vendor_id, vendor_name",
        "sql": "PK: vendor_id. sales_orders 테이블과 vendor_id로 조인하여 고객사별 매출/출고량 집계. vendor_name 기준 검색 및 고객사 단위 통계 보고 시 필수 조인 테이블."
    },
    {
        "id": "initial_inventory",
        "description": "2022년 말 기준 시스템 시작점의 초기 재고 스냅샷. '기초 재고', '초기 수량', '재고 시작점' 등 재고 계산의 출발 데이터를 필요로 할 때 검색됨.",
        "columns": "part_number, initial_quantity, stock_date",
        "sql": "PK: part_number (FK -> products). stock_date는 항상 '2022-12-31'. 현재고 = 기초 + 총입고 - 총출고 로직 구현 시 반드시 첫 번째 항으로 사용."
    },
    {
        "id": "current_products",
        "description": "현재 보유 중인 재고의 실시간 현황. '지금 창고에 몇 개 있는지', '현재 잔여 재고', 'on-hand' 수량을 물을 때 최우선으로 검색되는 요약 테이블.",
        "columns": "part_number, description, current_quantity, last_updated",
        "sql": "FK: part_number (references products). 입출고 이력을 매번 계산하지 않고 즉시 조회 가능한 최신 잔여 수량. last_updated 일자로 데이터 최신성 검증 가능."
    },
    {
        "id": "purchase_orders",
        "description": "부품 매입/입고 상세 이력. '입고된 수량', '구매 금액', '월별 입고량' 분석. 제조사별 매입 실적 추적 시 검색됨.",
        "columns": "purchase_id, manufacturer_id, part_number, purchase_quantity, purchase_date, actual_unit_cost",
        "sql": "PK: purchase_id. FK: part_number, manufacturer_id. 입고금액 합산: SUM(purchase_quantity * actual_unit_cost). 시점별 매입단가 추이 분석 가능."
    },
    {
        "id": "sales_orders",
        "description": "제품 출고/판매 상세 이력. '매출액', '판매 수량', '고객사별 납품량', '주간 매출' 분석. 실제 실적 데이터의 핵심.",
        "columns": "order_id, vendor_id, part_number, sale_quantity, sale_date, actual_selling_price",
        "sql": "PK: order_id. FK: part_number, vendor_id. 매출액 합산: SUM(sale_quantity * actual_selling_price). 기간별/고객사별 판매 실적 추적 시 필수."
    }
]