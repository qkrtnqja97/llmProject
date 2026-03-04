# 셀 3: 정적 데이터 정의
# ※ 예시/동의어/용어/스키마/에러패턴 추가 시 이 셀만 수정

"""
Few-shot SQL 예시 (질문-SQL 쌍)
- 질문 텍스트가 임베딩 대상(document)
- SQL은 메타데이터로 저장
"""

# ── 1. Few-shot SQL 예시 (질문-SQL 쌍) ──────────────────────
FEWSHOT_EXAMPLES = [
    # ==========================================
    # 1. 재고 및 제품 마스터 (Inventory & Products)
    # ==========================================
    {
        "q": "현재 재고 자산 가치가 가장 높은 상위 5개 품목",
        "sql": "SELECT cp.part_number, p.description, (cp.current_quantity * p.std_unit_cost) AS stock_value FROM current_products cp JOIN products p ON cp.part_number = p.part_number ORDER BY stock_value DESC LIMIT 5",
        "comment": "재고 수량과 표준 단가를 곱하여 자산 가치를 산출하고 정렬하는 로직입니다."
    },
    {
        "q": "재고가 10개 미만인 품목의 제조사 정보와 연락처",
        "sql": "SELECT p.part_number, m.name, m.contact_email FROM current_products cp JOIN products p ON cp.part_number = p.part_number JOIN purchase_orders po ON p.part_number = po.part_number JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id WHERE cp.current_quantity < 10 GROUP BY p.part_number, m.name, m.contact_email",
        "comment": "재고 부족 품목에 대해 발주를 위한 제조사 정보를 3중 조인으로 가져옵니다."
    },
    {
        "q": "카테고리별 아이템 수와 평균 재고 보유량",
        "sql": "SELECT p.description AS category, COUNT(*) AS item_count, ROUND(AVG(cp.current_quantity), 2) AS avg_stock FROM current_products cp JOIN products p ON cp.part_number = p.part_number GROUP BY p.description",
        "comment": "GROUP BY를 활용하여 카테고리(Description)별 통계치를 산출합니다."
    },
    {
        "q": "품번이 '80-'로 시작하는 제품의 총 재고 수량",
        "sql": "SELECT SUM(current_quantity) FROM current_products WHERE part_number LIKE '80-%'",
        "comment": "LIKE 연산자와 접두어를 활용하여 특정 제품군(Series)의 재고 합계를 구합니다."
    },

    # ==========================================
    # 2. 매출 및 시계열 분석 (Sales & Time-series)
    # ==========================================
    {
        "q": "올해 분기별 매출 현황",
        "sql": "SELECT EXTRACT(QUARTER FROM sale_date) AS quarter, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY quarter ORDER BY quarter",
        "comment": "EXTRACT를 사용하여 연도 내 분기별 실적을 집계합니다."
    },
    {
        "q": "최근 7일간 일별 판매 트렌드",
        "sql": "SELECT sale_date, SUM(sale_quantity * actual_selling_price) AS daily_rev FROM sales_orders WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY sale_date ORDER BY sale_date",
        "comment": "INTERVAL을 사용하여 동적인 최근 기간 데이터를 추출합니다."
    },
    {
        "q": "작년 대비 올해 매출 성장률(간이)",
        "sql": "SELECT year, revenue, (revenue - LAG(revenue) OVER (ORDER BY year)) / LAG(revenue) OVER (ORDER BY year) * 100 AS growth_rate FROM (SELECT EXTRACT(YEAR FROM sale_date) AS year, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders GROUP BY year) t",
        "comment": "윈도우 함수 LAG를 사용하여 이전 행(작년)과의 차이를 계산합니다."
    },
    {
        "q": "가장 비싸게 팔린 단일 주문 건 (TOP 1)",
        "sql": "SELECT order_id, part_number, (sale_quantity * actual_selling_price) AS total_amount FROM sales_orders ORDER BY total_amount DESC LIMIT 1",
        "comment": "산술 연산 결과값을 기준으로 최댓값을 조회합니다."
    },

    # ==========================================
    # 3. 고객사 및 제조사 분석 (Vendors & Manufacturers)
    # ==========================================
    {
        "q": "매출 기여도가 가장 높은 상위 3개 고객사(Vendor)",
        "sql": "SELECT v.vendor_name, SUM(so.sale_quantity * so.actual_selling_price) AS total_rev FROM sales_orders so JOIN vendors v ON so.vendor_id = v.vendor_id GROUP BY v.vendor_name ORDER BY total_rev DESC LIMIT 3",
        "comment": "거래처별 누적 매출액을 계산하여 우수 고객사를 파악합니다."
    },
    {
        "q": "특정 제조사(예: Intel) 제품의 총 판매 수량",
        "sql": "SELECT SUM(so.sale_quantity) FROM sales_orders so JOIN purchase_orders po ON so.part_number = po.part_number JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id WHERE m.name = 'Intel'",
        "comment": "판매 데이터와 매입/제조사 데이터를 연결하여 제조사별 판매량을 추적합니다."
    },
    {
        "q": "최근 1년간 주문이 한 번도 없었던 휴면 고객 리스트",
        "sql": "SELECT vendor_name FROM vendors WHERE vendor_id NOT IN (SELECT DISTINCT vendor_id FROM sales_orders WHERE sale_date >= CURRENT_DATE - INTERVAL '1 year')",
        "comment": "서브쿼리와 NOT IN을 사용하여 거래 단절 고객을 식별합니다."
    },
    {
        "q": "제조사별 평균 매입 리드타임(간이)",
        "sql": "SELECT m.name, AVG(po.actual_unit_cost) FROM purchase_orders po JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id GROUP BY m.name",
        "comment": "제조사별 매입 단가나 이력을 분석하는 기초 로직입니다."
    },

    # ==========================================
    # 4. 매입 및 단가 분석 (Purchase & Costing)
    # ==========================================
    {
        "q": "표준 원가보다 비싸게 매입한 사례 리스트",
        "sql": "SELECT po.order_id, po.part_number, p.std_unit_cost, po.actual_unit_cost FROM purchase_orders po JOIN products p ON po.part_number = p.part_number WHERE po.actual_unit_cost > p.std_unit_cost",
        "comment": "표준가와 실제 매입가를 비교하여 구매 효율성을 점검합니다."
    },
    {
        "q": "올해 총 매입액 현황",
        "sql": "SELECT SUM(purchase_quantity * actual_unit_cost) FROM purchase_orders WHERE EXTRACT(YEAR FROM purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)",
        "comment": "매입 주문 테이블에서 올해 지출된 총 비용을 합산합니다."
    },

    # ==========================================
    # 5. 비즈니스 인텔리전스 및 수익성 (BI & Profitability)
    # ==========================================
    {
        "q": "품목별 실질 마진율 분석 (상위 10개)",
        "sql": "SELECT so.part_number, ROUND(AVG((so.actual_selling_price - p.std_unit_cost) / NULLIF(so.actual_selling_price, 0) * 100), 2) AS margin_pct FROM sales_orders so JOIN products p ON so.part_number = p.part_number GROUP BY so.part_number ORDER BY margin_pct DESC LIMIT 10",
        "comment": "NULLIF로 0 나누기를 방지하며 평균 마진율을 계산합니다."
    },
    {
        "q": "재고 회전율 (최근 90일 판매량 / 현재 재고)",
        "sql": "SELECT cp.part_number, COALESCE(SUM(so.sale_quantity), 0) / NULLIF(cp.current_quantity, 0) AS turnover FROM current_products cp LEFT JOIN sales_orders so ON cp.part_number = so.part_number AND so.sale_date >= CURRENT_DATE - INTERVAL '90 days' GROUP BY cp.part_number, cp.current_quantity ORDER BY turnover DESC",
        "comment": "재고 대비 판매 속도를 측정하는 핵심 물류 지표입니다."
    },
    {
        "q": "ABC 분석 (매출 비중에 따른 등급 산정)",
        "sql": "WITH sales AS (SELECT part_number, SUM(sale_quantity * actual_selling_price) as rev FROM sales_orders GROUP BY part_number), total AS (SELECT part_number, rev, SUM(rev) OVER() as total_rev, SUM(rev) OVER(ORDER BY rev DESC) as cum_rev FROM sales) SELECT part_number, CASE WHEN cum_rev/total_rev <= 0.8 THEN 'A' WHEN cum_rev/total_rev <= 0.95 THEN 'B' ELSE 'C' END AS grade FROM total",
        "comment": "CTE와 윈도우 함수를 사용하여 매출 상위 80% 품목(A급)을 분류합니다."
    },
    {
        "q": "월별 평균 판매 단가(ASP) 추이",
        "sql": "SELECT DATE_TRUNC('month', sale_date) AS month, SUM(sale_quantity * actual_selling_price) / SUM(sale_quantity) AS asp FROM sales_orders GROUP BY month ORDER BY month",
        "comment": "총 매출을 총 수량으로 나누어 월별 평균 판매 가격의 흐름을 봅니다."
    },
    {
        "q": "수익 기여도가 가장 낮은 '느리게 움직이는' 제품",
        "sql": "SELECT p.part_number, cp.current_quantity FROM current_products cp JOIN products p ON cp.part_number = p.part_number WHERE NOT EXISTS (SELECT 1 FROM sales_orders so WHERE so.part_number = p.part_number AND so.sale_date >= CURRENT_DATE - INTERVAL '180 days')",
        "comment": "EXISTS를 활용해 최근 180일간 판매가 전혀 없는 악성 재고 후보를 찾습니다."
    },
    {
        "q": "가장 많은 종류의 부품을 공급하는 제조사",
        "sql": "SELECT m.name, COUNT(DISTINCT po.part_number) AS item_variety FROM manufacturers m JOIN purchase_orders po ON m.manufacturer_id = po.manufacturer_id GROUP BY m.name ORDER BY item_variety DESC LIMIT 1",
        "comment": "공급 품목의 다양성을 기준으로 제조사 영향력을 분석합니다."
    },
     # ==========================================
    # 6. 월별 매출액
    # ==========================================
    {
        "q": "2024년 월별 매출액",
        "sql": "SELECT TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') AS sales_month, COALESCE(SUM(so.sale_quantity * so.actual_selling_price), 0) AS monthly_revenue FROM inventory_mgmt.sales_orders AS so WHERE EXTRACT(YEAR FROM so.sale_date) = 2024 GROUP BY TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') ORDER BY sales_month"
    },
    {
        "q": "월별 매출액 현황",
        "sql": "SELECT TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') AS sales_month, COALESCE(SUM(so.sale_quantity * so.actual_selling_price), 0) AS monthly_revenue FROM inventory_mgmt.sales_orders AS so GROUP BY TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') ORDER BY sales_month DESC LIMIT 12"
    },
    {
        "q": "지난해 월별 매출액",
        "sql": "SELECT TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') AS sales_month, COALESCE(SUM(so.sale_quantity * so.actual_selling_price), 0) AS monthly_revenue FROM inventory_mgmt.sales_orders AS so WHERE EXTRACT(YEAR FROM so.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1 GROUP BY TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') ORDER BY sales_month"
    },
    {
        "q": "최근 12개월 월별 매출액",
        "sql": "SELECT TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') AS sales_month, COALESCE(SUM(so.sale_quantity * so.actual_selling_price), 0) AS monthly_revenue FROM inventory_mgmt.sales_orders AS so WHERE so.sale_date >= CURRENT_DATE - INTERVAL '12 months' GROUP BY TO_CHAR(DATE_TRUNC('month', so.sale_date), 'YYYY-MM') ORDER BY sales_month DESC"
    },

    # ==========================================
    # 7. 판매 횟수 (빈도) 분석
    # ==========================================
    {
        "q": "2024년 1년 동안 판매 횟수가 가장 많은 제품",
        "sql": """WITH Sales2024 AS (
    SELECT
        so.part_number,
        COUNT(DISTINCT so.order_id) AS sales_frequency
    FROM inventory_mgmt.sales_orders AS so
    WHERE so.sale_date >= '2024-01-01' AND so.sale_date < '2025-01-01'
    GROUP BY so.part_number
),
RankedProducts AS (
    SELECT
        s.part_number,
        s.sales_frequency,
        RANK() OVER (ORDER BY s.sales_frequency DESC) AS rn
    FROM Sales2024 AS s
)
SELECT
    rp.part_number,
    p.description,
    rp.sales_frequency
FROM RankedProducts AS rp
JOIN inventory_mgmt.products AS p ON rp.part_number = p.part_number
WHERE rp.rn = 1
ORDER BY rp.part_number""",
        "comment": "CTE + RANK()를 사용하여 2024년 기간에 가장 많이 주문된(판매 횟수 기준) 제품을 공동 1위 포함 조회합니다. 판매 횟수는 고유 order_id 건수로 계산합니다."
    },
    {
        "q": "올해 판매 횟수가 가장 많은 상위 5개 제품",
        "sql": """SELECT
    so.part_number,
    p.description,
    COUNT(DISTINCT so.order_id) AS sales_frequency
FROM inventory_mgmt.sales_orders AS so
JOIN inventory_mgmt.products AS p ON so.part_number = p.part_number
WHERE EXTRACT(YEAR FROM so.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY so.part_number, p.description
ORDER BY sales_frequency DESC
LIMIT 5""",
        "comment": "EXTRACT로 현재 연도를 동적 필터링하여 판매 횟수(order_id 건수) 기준 상위 5개 제품을 조회합니다."
    },
    {
        "q": "특정 연도(예: 2024년) 분기별 판매 횟수가 가장 많은 제품",
        "sql": """SELECT
    EXTRACT(QUARTER FROM so.sale_date) AS quarter,
    so.part_number,
    p.description,
    COUNT(DISTINCT so.order_id) AS sales_frequency
FROM inventory_mgmt.sales_orders AS so
JOIN inventory_mgmt.products AS p ON so.part_number = p.part_number
WHERE so.sale_date >= '2024-01-01' AND so.sale_date < '2025-01-01'
GROUP BY EXTRACT(QUARTER FROM so.sale_date), so.part_number, p.description
QUALIFY RANK() OVER (PARTITION BY EXTRACT(QUARTER FROM so.sale_date) ORDER BY sales_frequency DESC) = 1
ORDER BY quarter""",
        "comment": "분기(QUARTER)별로 PARTITION을 나눠 각 분기 내 판매 횟수 1위 제품을 도출합니다. QUALIFY를 지원하지 않는 DB는 CTE로 대체합니다."
    },
    {
        "q": "판매 횟수 기준 전체 제품 순위",
        "sql": """SELECT
    RANK() OVER (ORDER BY COUNT(DISTINCT so.order_id) DESC) AS sales_rank,
    so.part_number,
    p.description,
    COUNT(DISTINCT so.order_id) AS sales_frequency
FROM inventory_mgmt.sales_orders AS so
JOIN inventory_mgmt.products AS p ON so.part_number = p.part_number
GROUP BY so.part_number, p.description
ORDER BY sales_rank, so.part_number""",
        "comment": "RANK() 윈도우 함수로 전체 제품의 판매 횟수 순위를 산출합니다. 동점 제품은 동일 순위를 부여합니다."
    }
]

# ── 2. 동의어 사전 (한국어/오타 → 정식명) ───────────────────
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

# ── 3. 비즈니스 용어 정의 ────────────────────────────────────
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

# ── 4. 테이블-컬럼 Rich 문장 (스키마 설명) ── RAG 강화 버전 ──────────────────
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

# ── 5. 에러 → 해결책 패턴 ────────────────────────────────────
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

