"""
Few-shot SQL 예시 (질문-SQL 쌍)
- 질문 텍스트가 임베딩 대상(document)
- SQL은 메타데이터로 저장
"""

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
