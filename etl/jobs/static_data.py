# 셀 3: 정적 데이터 정의
# ※ 예시/동의어/용어/스키마/에러패턴 추가 시 이 셀만 수정

# ── 1. 동의어 사전 (한국어/오타 → 정식명) - Refine 단계 ───────────────────
SYNONYM_DATA = [
    {"term": "디지키", "canonical": "Digikey", "type": "vendor"},
    {"term": "마우저", "canonical": "Mouser", "type": "vendor"},
    {"term": "파넬", "canonical": "Farnell", "type": "vendor"},
    {"term": "알에스", "canonical": "RS", "type": "vendor"},
    {"term": "도시바", "canonical": "TOSHIBA", "type": "vendor"},
    {"term": "온세미", "canonical": "ON SEMI", "type": "vendor"},
    {"term": "온세미컨덕터", "canonical": "ON SEMI", "type": "vendor"},
    {"term": "롬", "canonical": "ROHM", "type": "vendor"},
    {"term": "서울반도체", "canonical": "SEOULSEMICON", "type": "vendor"},
    {"term": "에버라이트", "canonical": "EVERLIGHT", "type": "vendor"},
    {"term": "페어차일드", "canonical": "Fairchild", "type": "vendor"},
    {"term": "삼화", "canonical": "SAMWHA", "type": "vendor"},
    {"term": "산요", "canonical": "SANYO", "type": "vendor"},
    {"term": "신덴겐", "canonical": "SHINDENGEN", "type": "vendor"},
    {"term": "TEXAS INSTRUMENTS", "canonical": "TI", "type": "vendor"},
    {"term": "ST MICRO", "canonical": "ST", "type": "vendor"},
    {"term": "파나소닉", "canonical": "PANASONIC", "type": "manufacturer"},
    {"term": "인텔", "canonical": "INTEL", "type": "manufacturer"},
    {"term": "자일링스", "canonical": "XILINX", "type": "manufacturer"},
    {"term": "마이크론", "canonical": "MICRON", "type": "manufacturer"},
    {"term": "브로드컴", "canonical": "BROADCOM", "type": "manufacturer"},
    {"term": "인피니온", "canonical": "INFINEON", "type": "manufacturer"},
    {"term": "마벨", "canonical": "MARVELL", "type": "manufacturer"},
    {"term": "사이프레스", "canonical": "CYPRESS", "type": "manufacturer"},
    {"term": "티아이", "canonical": "TI", "type": "manufacturer"},
    {"term": "아나로그디바이스", "canonical": "ADI", "type": "manufacturer"},
    {"term": "프리스케일", "canonical": "FREESCALE", "type": "manufacturer"},
    {"term": "맥심", "canonical": "MAXIM", "type": "manufacturer"},
    {"term": "소니", "canonical": "SONY", "type": "manufacturer"},
    {"term": "샤프", "canonical": "SHARP", "type": "manufacturer"},
    {"term": "르네사스", "canonical": "RENESAS", "type": "manufacturer"},
    {"term": "옴론", "canonical": "OMRON", "type": "manufacturer"},
    {"term": "모토로라", "canonical": "MOTOROLA", "type": "manufacturer"},
    {"term": "BROADCO", "canonical": "BROADCOM", "type": "manufacturer"},
    {"term": "BROMDCOM", "canonical": "BROADCOM", "type": "manufacturer"},
    {"term": "BRPADCOM", "canonical": "BROADCOM", "type": "manufacturer"},
    {"term": "CONEXAN", "canonical": "CONEXANT", "type": "manufacturer"},
    {"term": "INETL", "canonical": "INTEL", "type": "manufacturer"},
    {"term": "MARVEL", "canonical": "MARVELL", "type": "manufacturer"},
    {"term": "CYRRUS", "canonical": "CIRRUS", "type": "manufacturer"},
    {"term": "CAVINMN", "canonical": "CAVIUM", "type": "manufacturer"},
    {"term": "ENTROPI", "canonical": "ENTROPIC", "type": "manufacturer"},
    {"term": "ETRONTE", "canonical": "ENTROPIC", "type": "manufacturer"},
    {"term": "NUMONVX", "canonical": "NUMONYX", "type": "manufacturer"},
    {"term": "RENASAS", "canonical": "RENESAS", "type": "manufacturer"},
    {"term": "Altair", "canonical": "ALTAIR", "type": "manufacturer"},
    {"term": "Infineon", "canonical": "INFINEON", "type": "manufacturer"},
    {"term": "Lattice", "canonical": "LATTICE", "type": "manufacturer"},
    {"term": "Microchip", "canonical": "MICROCHIP", "type": "manufacturer"},
    {"term": "IC칩", "canonical": "IC", "type": "category"},
    {"term": "집적회로", "canonical": "IC", "type": "category"},
    {"term": "반도체", "canonical": "IC", "type": "category"},
    {"term": "커패시터", "canonical": "C_CHIP/CAP", "type": "category"},
    {"term": "캐패시터", "canonical": "C_CHIP/CAP", "type": "category"},
    {"term": "콘덴서", "canonical": "C_CHIP/CAP", "type": "category"},
    {"term": "저항", "canonical": "R_CHIP/RES", "type": "category"},
    {"term": "레지스터", "canonical": "R_CHIP/RES", "type": "category"},
    {"term": "고객사", "canonical": "vendors", "type": "table_alias"},
    {"term": "판매처", "canonical": "vendors", "type": "table_alias"},
    {"term": "거래처", "canonical": "vendors", "type": "table_alias"},
    {"term": "바이어", "canonical": "vendors", "type": "table_alias"},
    {"term": "공급사", "canonical": "manufacturers", "type": "table_alias"},
    {"term": "제조사", "canonical": "manufacturers", "type": "table_alias"},
    {"term": "납품처", "canonical": "manufacturers", "type": "table_alias"},
    {"term": "벤더", "canonical": "manufacturers", "type": "table_alias"},
    {"term": "ASP", "canonical": "평균판매단가", "type": "bizterm"},
    {"term": "YoY", "canonical": "전년동기대비", "type": "bizterm"},
    {"term": "MoM", "canonical": "전월대비", "type": "bizterm"},
    {"term": "단가", "canonical": "실제단가", "type": "column_hint"},
]

# ── 2. Few-shot SQL 예시 (질문-SQL 쌍) - SQLGEN 단계 ──────────────────────
FEWSHOT_EXAMPLES = [

    # ==========================================
    # 1. 재고 및 제품 마스터
    # ==========================================

    {
        "q": "현재 재고 자산 가치가 가장 높은 상위 5개 품목",
        "sql": "SELECT cp.part_number, p.description, (cp.current_quantity * p.std_unit_cost) AS stock_value FROM current_products cp JOIN products p ON cp.part_number = p.part_number ORDER BY stock_value DESC LIMIT 5",
        "comment": "재고 수량과 표준 단가를 곱하여 자산 가치를 산출하고 정렬"
    },

    {
        "q": "재고가 10개 미만인 품목의 제조사 정보와 연락처",
        "sql": "SELECT p.part_number, m.name, m.contact_email FROM current_products cp JOIN products p ON cp.part_number = p.part_number JOIN purchase_orders po ON p.part_number = po.part_number JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id WHERE cp.current_quantity < 10 GROUP BY p.part_number, m.name, m.contact_email",
        "comment": "재고 부족 품목에 대한 제조사 정보 조회"
    },

    {
        "q": "카테고리별 아이템 수와 평균 재고 보유량",
        "sql": "SELECT p.description AS category, COUNT(*) AS item_count, ROUND(AVG(cp.current_quantity),2) AS avg_stock FROM current_products cp JOIN products p ON cp.part_number = p.part_number GROUP BY p.description",
        "comment": "카테고리별 재고 통계"
    },

    {
        "q": "품번이 '80-'로 시작하는 제품의 총 재고 수량",
        "sql": "SELECT SUM(current_quantity) FROM current_products WHERE part_number LIKE '80-%'",
        "comment": "LIKE 접두어 검색"
    },


    # ==========================================
    # 2. 매출 분석
    # ==========================================

    {
        "q": "올해 분기별 매출 현황",
        "sql": "SELECT EXTRACT(QUARTER FROM sale_date) AS quarter, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date)=EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY quarter ORDER BY quarter",
        "comment": "분기별 매출 집계"
    },

    {
        "q": "최근 7일간 일별 판매 트렌드",
        "sql": "SELECT sale_date, SUM(sale_quantity * actual_selling_price) AS daily_rev FROM sales_orders WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY sale_date ORDER BY sale_date",
        "comment": "최근 기간 매출 트렌드"
    },

    {
        "q": "가장 비싸게 팔린 단일 주문 건",
        "sql": "SELECT order_id, part_number, (sale_quantity * actual_selling_price) AS total_amount FROM sales_orders ORDER BY total_amount DESC LIMIT 1",
        "comment": "최대 주문 금액"
    },


    # ==========================================
    # 3. 고객 / 제조사 분석
    # ==========================================

    {
        "q": "매출 기여도가 가장 높은 상위 3개 고객사",
        "sql": "SELECT v.vendor_name, SUM(so.sale_quantity * so.actual_selling_price) AS total_rev FROM sales_orders so JOIN vendors v ON so.vendor_id = v.vendor_id GROUP BY v.vendor_name ORDER BY total_rev DESC LIMIT 3",
        "comment": "고객사별 매출 분석"
    },

    {
        "q": "특정 제조사 제품의 총 판매 수량",
        "sql": "SELECT SUM(so.sale_quantity) FROM sales_orders so JOIN purchase_orders po ON so.part_number = po.part_number JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id WHERE m.name = 'Intel'",
        "comment": "제조사별 판매량"
    },


    # ==========================================
    # 4. 비용 / 매입 분석
    # ==========================================

    {
        "q": "표준 원가보다 비싸게 매입한 사례",
        "sql": "SELECT po.purchase_id, po.part_number, p.std_unit_cost, po.actual_unit_cost FROM purchase_orders po JOIN products p ON po.part_number = p.part_number WHERE po.actual_unit_cost > p.std_unit_cost",
        "comment": "매입 단가 비교"
    },

    {
        "q": "올해 총 매입액",
        "sql": "SELECT SUM(purchase_quantity * actual_unit_cost) FROM purchase_orders WHERE EXTRACT(YEAR FROM purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)",
        "comment": "연간 매입 비용"
    },


    # ==========================================
    # 5. BI 분석
    # ==========================================

    {
        "q": "품목별 실질 마진율 상위 10개",
        "sql": "SELECT so.part_number, ROUND(AVG((so.actual_selling_price - p.std_unit_cost) / NULLIF(so.actual_selling_price,0) * 100),2) AS margin_pct FROM sales_orders so JOIN products p ON so.part_number = p.part_number GROUP BY so.part_number ORDER BY margin_pct DESC LIMIT 10",
        "comment": "마진율 분석"
    },

    {
        "q": "재고 회전율",
        "sql": "SELECT cp.part_number, COALESCE(SUM(so.sale_quantity),0) / NULLIF(cp.current_quantity,0) AS turnover FROM current_products cp LEFT JOIN sales_orders so ON cp.part_number = so.part_number AND so.sale_date >= CURRENT_DATE - INTERVAL '90 days' GROUP BY cp.part_number, cp.current_quantity ORDER BY turnover DESC",
        "comment": "재고 대비 판매 속도"
    },


    # ==========================================
    # 6. 월별 매출
    # ==========================================

    {
        "q": "월별 매출액",
        "sql": "SELECT DATE_TRUNC('month', sale_date) AS month, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders GROUP BY month ORDER BY month",
        "comment": "월별 매출 추이"
    }

]

# ── 3. 비즈니스 용어 정의 - SQLGEN 단계 ────────────────────────────────────
BIZTERM_DATA = [
            {"id": "term_inv_turnover", "description": "재고회전율", "metadatas": {"sql": "보유 재고가 일정 기간 동안 몇 번이나 판매되었는지 나타내는 지표로, 수치가 높을수록 재고가 효율적으로 관리되고 있음을 의미함."}},
            {"id": "term_margin_rate", "description": "마진율", "metadatas": {"sql": "판매 가격에서 원가를 제외한 이익이 판매가에서 차지하는 비중으로, 수익성을 판단하는 핵심 지표."}},
            {"id": "term_dead_stock", "description": "데드스톡", "metadatas": {"sql": "장기간 거래나 판매가 발생하지 않아 창고 점유 비용만 발생시키는 악성 재고."}},
            {"id": "term_gross_profit", "description": "매출총이익", "metadatas": {"sql": "전체 매출액에서 물품 매입에 들어간 원가를 차감한 순수 이익 금액."}},
            {"id": "term_abc_analysis", "description": "ABC분석", "metadatas": {"sql": "매출 기여도에 따라 품목을 A(중요), B(보통), C(낮음) 등급으로 분류하여 관리 우선순위를 정하는 분석 기법."}},
            {"id": "term_purchase_price", "description": "매입단가", "metadatas": {"sql": "상품을 들여올 때 지불하는 개당 비용으로, 상황에 따라 실제 매입가 또는 사전에 정해진 표준 원가를 적용함."}},
            {"id": "term_sales_price", "description": "판매단가", "metadatas": {"sql": "상품을 판매할 때 고객에게 청구하는 개당 가격으로, 실제 거래가 또는 고정된 표준 판매가를 의미함."}},
            {"id": "term_safety_stock", "description": "안전재고", "metadatas": {"sql": "예상치 못한 수요 변동이나 공급 지연에 대비하여 품절을 방지하기 위해 상시 보유해야 하는 최소한의 재고 수준."}},
            {"id": "term_reorder_point", "description": "발주점", "metadatas": {"sql": "재고 부족이 발생하기 전에 새로운 주문을 진행해야 하는 기준이 되는 재고 수량."}},
            {"id": "term_lead_time", "description": "리드타임", "metadatas": {"sql": "물품을 주문(발주)한 시점부터 실제로 창고에 입고되기까지 소요되는 전체 기간."}},
            {"id": "term_profitability", "description": "수익성", "metadatas": {"sql": "판매 수익에서 모든 비용을 제외하고 남은 이익의 수준을 통해 기업의 운영 효율을 평가하는 기준."}},
            {"id": "term_revenue", "description": "매출액", "metadatas": {"sql": "특정 기간 동안 상품 판매 활동을 통해 발생한 전체 판매 금액의 합계."}},
            {"id": "term_purchase_amount", "description": "매입액", "metadatas": {"sql": "특정 기간 동안 상품 확보를 위해 지출한 전체 구매 금액의 합계."}},
            {"id": "term_asp", "description": "ASP", "metadatas": {"sql": "평균 판매 단가. 전체 매출액을 총 판매 수량으로 나눈 값으로, 품목당 평균적으로 얼마에 판매되었는지 나타냄."}},
            {"id": "term_yoy", "description": "YoY", "metadatas": {"sql": "전년 동기 대비 증감률. 작년의 동일한 기간과 현재의 실적을 비교하여 성장세를 분석하는 방식."}},
            {"id": "term_winter_snap", "description": "윈터-스냅", "metadatas": {"sql": "2022년 말 기준의 초기 재고 데이터로, 모든 재고 흐름 분석과 수량 검증의 절대적인 시작점이 되는 데이터."}},
            {"id": "term_wed_fri_wave", "description": "수금-웨이브", "metadatas": {"sql": "매주 수요일과 금요일에 정기적으로 발생하는 대규모 물류 출고 흐름을 의미함."}},
            {"id": "term_dark_10", "description": "다크-텐", "metadatas": {"sql": "장기간 입출고 이력이 전혀 없는 하위 10%의 품목군으로, 창고 효율을 저하시키는 주요 집중 관리 대상."}},
            {"id": "term_fortnight_batch", "description": "보름-배치", "metadatas": {"sql": "매월 1일과 15일에 집중적으로 대량 입고가 진행되는 정기 발주 및 매입 주기."}},
            {"id": "term_ghost_pn", "description": "고스트-피엔", "metadatas": {"sql": "시스템 마스터에는 등록되어 있으나 실제 거래가 한 번도 발생하지 않아 데이터상으로만 존재하는 품목."}},
            {"id": "term_delta_check", "description": "델타-체크", "metadatas": {"sql": "실제 창고의 재고 수량과 장부상의 계산 수량이 일치하는지 대조하여 데이터의 무결성을 검증하는 작업."}},
            {"id": "term_golden_margin", "description": "골든-마진", "metadatas": {"sql": "초기 가격보다 실제 판매가가 더 높게 책정되어 수익이 극대화된 우수한 계약 또는 판매 상태."}},
            {"id": "term_unique_lock", "description": "유니크-락", "metadatas": {"sql": "중복 등록 방지 제약으로 인해 동일한 업체가 신규로 등록되는 것을 차단하여 데이터 정합성을 유지하는 상태."}},
            {"id": "term_zero_base_violation", "description": "제로-베이스 위반", "metadatas": {"sql": "구매 이력보다 판매 날짜가 앞서는 등 시간적 선후 관계가 맞지 않는 논리적 데이터 오류 상태."}},
            {"id": "term_unit_tagging", "description": "유닛-태깅", "metadatas": {"sql": "분기별 예산 수립을 위해 표준 매입 원가를 확정하고 관리 기준을 설정하는 행위."}}
        ]  

# ── 4. 테이블-컬럼 Rich 문장 (스키마 설명) - SQLGEN 단계 ──────────────────
TABLE_SCHEMA_DATA = [
            {
                "id": "products",
                "description": "제품 마스터, 부품 목록, 파트 넘버(part_number), 카테고리(IC, FET, TR, C_CHIP), 반도체 규격, 표준 단가(cost), 가격 정보. 제품의 이름, 종류, 단가를 묻는 질문에 참조.",
                "metadatas": {
                    "columns": "part_number, description, std_unit_cost, std_selling_price",
                    "sql": "PK: part_number. 'description'은 카테고리 정보임. 제품 상세 정보 조회 및 거래 테이블 조인 시 기준 테이블로 사용."
                }
            },
            {
                "id": "manufacturers",
                "description": "제조사, 공급처, 납품 업체, 부품 생산자 정보. '물건을 어디서 가져왔나?', '특정 제조사 납품 현황' 파악 시 사용.",
                "metadatas": {
                    "columns": "manufacturer_id, name",
                    "sql": "PK: manufacturer_id. purchase_orders와 조인하여 업체명(name) 검색 및 공급처별 통계 집계 시 사용."
                }
            },
            {
                "id": "vendors",
                "description": "고객사, 판매처, 거래처, 바이어, 납품처 리스트. '어디로 판매했나?', '고객사별 매출 실적' 분석 시 필수 참조.",
                "metadatas": {
                    "columns": "vendor_id, vendor_name",
                    "sql": "PK: vendor_id. sales_orders와 조인하여 고객사명(vendor_name) 검색 및 매출 통계 보고 시 사용."
                }
            },
            {
                "id": "initial_inventory",
                "description": "기초 재고, 2022년 말 초기 수량, 재고 시작점 스냅샷. 현재고 계산을 위한 과거 시작 수량 데이터.",
                "metadatas": {
                    "columns": "part_number, initial_quantity, stock_date",
                    "sql": "PK: part_number. stock_date='2022-12-31' 고정. 수식: (기초재고 + 입고합계 - 출고합계)의 기초 데이터."
                }
            },
            {
                "id": "current_products",
                "description": "실시간 현재고, 창고 잔량, 보유 개수. 계산 없이 '지금 현재' 수량만 빠르게 보고 싶을 때 사용.",
                "metadatas": {
                    "columns": "part_number, description, current_quantity, last_updated",
                    "sql": "FK: part_number. 계산 없이 현재 시점의 재고 보유량(current_quantity)을 직접 조회할 때 사용."
                }
            },
            {
                "id": "purchase_orders",
                "description": "매입 내역, 입고 이력, 구매 기록, 입고 금액, 월별 매입 현황. 지출 및 물건 도입 기록 분석 시 사용.",
                "metadatas": {
                    "columns": "purchase_id, manufacturer_id, part_number, purchase_quantity, purchase_date, actual_unit_cost",
                    "sql": "PK: purchase_id. 매입액 계산: SUM(purchase_quantity * actual_unit_cost). 기간별/업체별 매입 분석용."
                }
            },
            {
                "id": "sales_orders",
                "description": "출고 내역, 판매 이력, 매출 실적, 판매 금액, 고객사 납품량, 월별/주간 매출 분석. 판매 실적 추적 시 사용.",
                "metadatas": {
                    "columns": "order_id, vendor_id, part_number, sale_quantity, sale_date, actual_selling_price",
                    "sql": "PK: order_id. 매출액 계산: SUM(sale_quantity * actual_selling_price). 기간별/고객사별 판매 실적 분석용."
                }
            }
        ]

# ── 5. 에러 → 해결책 패턴 - Retry Error 단계 ────────────────────────────────────
ERROR_PATTERN_DATA = [
    {
        "doc": "에러: column last_updated does not exist 또는 WHERE last_updated 조건 사용. 원인: current_products는 스냅샷 테이블로 날짜 필터 금지. 해결: WHERE last_updated 조건 전부 제거하고 전체 조회",
        "meta": {"error_type": "date_filter_on_snapshot", "table": "current_products"}
    },
    {
        "doc": "에러: column std_unit_cost does not exist in sales_orders. 원인: std_unit_cost는 products 테이블 컬럼. 해결: products 테이블과 JOIN 후 p.std_unit_cost 사용",
        "meta": {"error_type": "wrong_table_column", "table": "sales_orders"}
    },
    {
        "doc": "에러: operator does not exist integer = character varying. 원인: vendor_id/manufacturer_id(INTEGER)를 문자열과 비교. 해결: WHERE vendor_id = 2 처럼 정수로 비교하거나 vendors JOIN으로 vendor_name 비교",
        "meta": {"error_type": "type_mismatch", "table": "vendors"}
    },
    {
        "doc": "에러: invalid input syntax for type date. 원인: 날짜를 잘못된 형식으로 입력. 해결: DATE 타입은 'YYYY-MM-DD' 형식 문자열 사용. 예: '2024-01-01'",
        "meta": {"error_type": "invalid_date_format", "table": "sales_orders"}
    },
    {
        "doc": "에러: column vendor_name does not exist in sales_orders. 원인: vendor_name은 vendors 테이블 컬럼. 해결: JOIN vendors v ON so.vendor_id=v.vendor_id 후 v.vendor_name 사용",
        "meta": {"error_type": "missing_join", "table": "vendors"}
    },
    {
        "doc": "에러: column name does not exist in purchase_orders. 원인: 제조사명(name)은 manufacturers 테이블 컬럼. 해결: JOIN manufacturers m ON po.manufacturer_id=m.manufacturer_id 후 m.name 사용",
        "meta": {"error_type": "missing_join", "table": "manufacturers"}
    },
    {
        "doc": "에러: aggregate functions are not allowed in WHERE. 원인: WHERE절에 SUM/AVG 등 집계함수 사용. 해결: HAVING절로 이동. 예: GROUP BY ... HAVING SUM(sale_quantity) > 100",
        "meta": {"error_type": "aggregate_in_where", "table": "sales_orders"}
    },
    {
        "doc": "에러: column part_number is ambiguous. 원인: 여러 테이블에 part_number가 있어서 어느 테이블인지 불명확. 해결: 테이블 별칭 명시. 예: cp.part_number, so.part_number",
        "meta": {"error_type": "ambiguous_column", "table": "multiple"}
    },
    {
        "doc": "에러: division by zero 또는 CASE WHEN current_quantity=0. 원인: 재고회전율 등 나눗셈 시 분모가 0. 해결: CASE WHEN current_quantity > 0 THEN ... ELSE NULL END 또는 NULLIF(current_quantity, 0) 사용",
        "meta": {"error_type": "division_by_zero", "table": "current_products"}
    },
    {
        "doc": "에러: 결과가 0건인데 데이터가 있어야 함. 원인: 제조사/고객사 이름 오타 또는 대소문자 불일치. 해결: BROADCOM 조회 시 IN ('BROADCOM','BROADCO','BROMDCOM','BRPADCOM') 처럼 오타변형 포함. UPPER() 함수로 대소문자 통일",
        "meta": {"error_type": "name_typo_zero_result", "table": "manufacturers"}
    },
    {
        "doc": "에러: syntax error at or near SELECT 또는 ANSI escape code 포함. 원인: LLM이 SQL에 마크다운 코드블록이나 이스케이프 코드를 포함. 해결: ```sql 제거, \\x1b[ 제거 후 순수 SQL만 추출",
        "meta": {"error_type": "sql_format_error", "table": "none"}
    },
    {
        "doc": "에러: relation current_products does not exist. 원인: search_path 미설정. 해결: SET search_path TO inventory_mgmt 실행 후 쿼리",
        "meta": {"error_type": "schema_not_set", "table": "current_products"}
    },
    {
        "doc": "에러: column must appear in the GROUP BY clause or be used in an aggregate function. 원인: 집계 함수(SUM/AVG 등) 외의 SELECT 컬럼이 GROUP BY에 누락됨. 해결: SELECT에 명시된 비집계 컬럼을 모두 GROUP BY 절에 추가",
        "meta": {"error_type": "missing_group_by", "table": "multiple"}
    },
    {
        "doc": "에러: 컬럼 소속 오류 또는 복합 질문에서 CTE JOIN 후 전체 집계 발생. 원인: 차이 최대/최소 제품을 특정하지 않고 전체 재고를 대상으로 집계하거나, CROSS JOIN/UNION ALL 사용. 해결: max_part/min_part CTE로 part_number를 먼저 추출하고 WHERE so.part_number = (SELECT part_number FROM max_part) 로 필터링. 최종 SELECT는 스칼라 서브쿼리로 한 행 출력. CROSS JOIN 절대 금지",
        "meta": {"error_type": "complex_cte_filter", "table": "multiple"}
    },
    {
        "doc": "에러: 테이블 'inventory_diff' DB에 없음. 원인: CTE 이름이 CamelCase(InventoryDiff)로 정의됐는데 본문에서 snake_case(inventory_diff)로 참조하거나, CTE 정의 전에 참조함. 해결: CTE 이름과 참조명을 동일하게 통일하고, WITH절에서 정의된 이름 그대로 사용",
        "meta": {"error_type": "cte_name_mismatch", "table": "multiple"}
    },
    {
        "doc": "에러: manufacturers 테이블에서 manufacturer_name 컬럼 없음. 원인: manufacturers 테이블의 업체명 컬럼명 환각. 해결: manufacturers 테이블의 업체명 컬럼은 반드시 m.name 사용. manufacturer_name 컬럼은 존재하지 않음",
        "meta": {"error_type": "wrong_column_name", "table": "manufacturers"}
    },
]

# ── 6. 핵심 키워드 → 의도 매핑 ──────────────────────────────
KEYWORD_INTENT_DATA = [
    {
        "doc": "재고 현황 조회 키워드: 재고 보유 수량 남은거 얼마나있어 현재 지금 인벤토리 stock inventory. 사용테이블: current_products. 주의: 날짜필터 금지",
        "meta": {"intent": "stock_query", "table": "current_products"}
    },
    {
        "doc": "매출 조회 키워드: 매출 판매 팔린 revenue sales 실적 얼마팔았 주문 얼마벌었. 사용테이블: sales_orders JOIN vendors. 날짜컬럼: sale_date",
        "meta": {"intent": "sales_query", "table": "sales_orders"}
    },
    {
        "doc": "매입 구매 조회 키워드: 매입 구매 발주 납품 원가 purchase 얼마샀 비용. 사용테이블: purchase_orders JOIN manufacturers. 날짜컬럼: purchase_date",
        "meta": {"intent": "purchase_query", "table": "purchase_orders"}
    },
    {
        "doc": "수익성 분석 키워드: 마진 이익 수익 남는거 profit margin 총이익 gross. 사용테이블: sales_orders JOIN products. 계산: actual_selling_price - std_unit_cost",
        "meta": {"intent": "profit_query", "table": "sales_orders+products"}
    },
    {
        "doc": "고객사 분석 키워드: 고객사 판매처 거래처 바이어 누가많이샀 어디서 vendor client customer. 사용테이블: sales_orders JOIN vendors",
        "meta": {"intent": "vendor_query", "table": "vendors"}
    },
    {
        "doc": "제조사 분석 키워드: 제조사 공급사 납품처 어디서샀 supplier maker manufacturer. 사용테이블: purchase_orders JOIN manufacturers",
        "meta": {"intent": "manufacturer_query", "table": "manufacturers"}
    },
    {
        "doc": "기간 필터 키워드: 이번달 저번달 올해 작년 최근 지난 n개월 분기 연도 월별. 사용컬럼: sale_date(매출) purchase_date(매입). DATE_TRUNC EXTRACT INTERVAL 사용",
        "meta": {"intent": "date_filter", "table": "sales_orders+purchase_orders"}
    },
    {
        "doc": "랭킹 순위 키워드: 탑 상위 하위 많은 적은 1등 베스트 워스트 top bottom rank. 사용절: ORDER BY ... DESC/ASC LIMIT n",
        "meta": {"intent": "ranking_query", "table": "multiple"}
    },
    {
        "doc": "재고회전율 데드스톡 키워드: 재고회전율 turnover 안팔리는 오래된 묵은 데드스톡 dead stock 느린. 사용테이블: current_products LEFT JOIN sales_orders",
        "meta": {"intent": "turnover_deadstock", "table": "current_products+sales_orders"}
    },
    {
        "doc": "ABC분석 키워드: ABC분석 abc 파레토 pareto 기여도 중요도 등급 분류 80 20. 사용테이블: sales_orders. 윈도우함수: SUM OVER ORDER BY",
        "meta": {"intent": "abc_analysis", "table": "sales_orders"}
    },
    {
        "doc": "성장률/증감 비교 키워드: 성장률 증가 감소 대비 YoY MoM 추세 트렌드. 사용테이블: sales_orders (매출기준). 기간을 분리하여 CTE(WITH절)로 집계 후 증감 계산",
        "meta": {"intent": "growth_analysis", "table": "sales_orders"}
    },
]