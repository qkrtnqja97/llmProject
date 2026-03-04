# 셀 3: 정적 데이터 정의
# ※ 예시/동의어/용어/스키마/에러패턴 추가 시 이 셀만 수정

# ── 1. Few-shot SQL 예시 (질문-SQL 쌍) ──────────────────────
FEWSHOT_EXAMPLES = [
    {
        "q": "지금 재고 제일 많은 품목",
        "sql": "SELECT cp.part_number, p.description, cp.current_quantity FROM current_products cp JOIN products p ON cp.part_number=p.part_number ORDER BY cp.current_quantity DESC LIMIT 1"
    },
    {
        "q": "재고 상위 10개 품목",
        "sql": "SELECT cp.part_number, p.description, cp.current_quantity FROM current_products cp JOIN products p ON cp.part_number=p.part_number ORDER BY cp.current_quantity DESC LIMIT 10"
    },
    {
        "q": "재고 하위 10개 품목",
        "sql": "SELECT cp.part_number, p.description, cp.current_quantity FROM current_products cp JOIN products p ON cp.part_number=p.part_number ORDER BY cp.current_quantity ASC LIMIT 10"
    },
    {
        "q": "재고 없는 품목",
        "sql": "SELECT cp.part_number, p.description FROM current_products cp JOIN products p ON cp.part_number=p.part_number WHERE cp.current_quantity=0"
    },
    {
        "q": "재고 100개 미만 품목",
        "sql": "SELECT cp.part_number, p.description, cp.current_quantity FROM current_products cp JOIN products p ON cp.part_number=p.part_number WHERE cp.current_quantity < 100 ORDER BY cp.current_quantity ASC"
    },
    {
        "q": "전체 재고 총 수량",
        "sql": "SELECT SUM(current_quantity) AS total_stock FROM current_products"
    },
    {
        "q": "전체 재고 자산 가치",
        "sql": "SELECT SUM(cp.current_quantity * p.std_unit_cost) AS stock_value FROM current_products cp JOIN products p ON cp.part_number=p.part_number"
    },
    {
        "q": "카테고리별 재고 현황",
        "sql": "SELECT p.description AS category, COUNT(*) AS item_count, SUM(cp.current_quantity) AS total_qty FROM current_products cp JOIN products p ON cp.part_number=p.part_number GROUP BY p.description ORDER BY total_qty DESC"
    },
    {
        "q": "IC 재고 현황",
        "sql": "SELECT cp.part_number, cp.current_quantity FROM current_products cp WHERE cp.description='IC' ORDER BY cp.current_quantity DESC"
    },
    {
        "q": "C_CHIP/CAP 재고 현황",
        "sql": "SELECT cp.part_number, cp.current_quantity FROM current_products cp WHERE cp.description='C_CHIP/CAP' ORDER BY cp.current_quantity DESC"
    },
    {
        "q": "R_CHIP/RES 재고 현황",
        "sql": "SELECT cp.part_number, cp.current_quantity FROM current_products cp WHERE cp.description='R_CHIP/RES' ORDER BY cp.current_quantity DESC"
    },
    {
        "q": "데드스톡 품목",
        "sql": "SELECT cp.part_number, p.description, cp.current_quantity FROM current_products cp JOIN products p ON cp.part_number=p.part_number WHERE cp.part_number NOT IN (SELECT DISTINCT part_number FROM sales_orders WHERE sale_date >= CURRENT_DATE - INTERVAL '6 months') AND cp.current_quantity > 0 ORDER BY cp.current_quantity DESC"
    },
    {
        "q": "이번달 매출 총액",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS total_revenue FROM sales_orders WHERE DATE_TRUNC('month', sale_date)=DATE_TRUNC('month', CURRENT_DATE)"
    },
    {
        "q": "저번달 매출 총액",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS total_revenue FROM sales_orders WHERE DATE_TRUNC('month', sale_date)=DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')"
    },
    {
        "q": "올해 매출 총액",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS total_revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date)=EXTRACT(YEAR FROM CURRENT_DATE)"
    },
    {
        "q": "작년 매출 총액",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS total_revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date)=EXTRACT(YEAR FROM CURRENT_DATE)-1"
    },
    {
        "q": "2024년 월별 매출 추이",
        "sql": "SELECT DATE_TRUNC('month', sale_date) AS month, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date)=2024 GROUP BY month ORDER BY month"
    },
    {
        "q": "2023년 월별 매출 추이",
        "sql": "SELECT DATE_TRUNC('month', sale_date) AS month, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date)=2023 GROUP BY month ORDER BY month"
    },
    {
        "q": "최근 3개월 매출 비교",
        "sql": "SELECT DATE_TRUNC('month', sale_date) AS month, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE sale_date >= CURRENT_DATE - INTERVAL '3 months' GROUP BY month ORDER BY month"
    },
    {
        "q": "올해 vs 작년 매출 비교",
        "sql": "SELECT EXTRACT(YEAR FROM sale_date) AS year, SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date) >= EXTRACT(YEAR FROM CURRENT_DATE)-1 GROUP BY year ORDER BY year"
    },
    {
        "q": "가장 많이 팔린 품목 탑 10",
        "sql": "SELECT so.part_number, p.description, SUM(so.sale_quantity) AS total_qty FROM sales_orders so JOIN products p ON so.part_number=p.part_number GROUP BY so.part_number, p.description ORDER BY total_qty DESC LIMIT 10"
    },
    {
        "q": "매출액 상위 품목 탑 10",
        "sql": "SELECT so.part_number, p.description, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN products p ON so.part_number=p.part_number GROUP BY so.part_number, p.description ORDER BY revenue DESC LIMIT 10"
    },
    {
        "q": "카테고리별 매출 현황",
        "sql": "SELECT p.description AS category, SUM(so.sale_quantity) AS total_qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN products p ON so.part_number=p.part_number GROUP BY p.description ORDER BY revenue DESC"
    },
    {
        "q": "매출 가장 많은 고객사 탑 5",
        "sql": "SELECT v.vendor_name, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id GROUP BY v.vendor_name ORDER BY revenue DESC LIMIT 5"
    },
    {
        "q": "고객사별 매출 현황 전체",
        "sql": "SELECT v.vendor_name, COUNT(DISTINCT so.order_id) AS order_count, SUM(so.sale_quantity) AS total_qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id GROUP BY v.vendor_name ORDER BY revenue DESC"
    },
    {
        "q": "Digikey 매출 현황",
        "sql": "SELECT so.part_number, p.description, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id JOIN products p ON so.part_number=p.part_number WHERE v.vendor_name='Digikey' GROUP BY so.part_number, p.description ORDER BY revenue DESC"
    },
    {
        "q": "Mouser 매출 현황",
        "sql": "SELECT so.part_number, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id WHERE v.vendor_name='Mouser' GROUP BY so.part_number ORDER BY revenue DESC"
    },
    {
        "q": "Farnell 매출 현황",
        "sql": "SELECT so.part_number, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id WHERE v.vendor_name='Farnell' GROUP BY so.part_number ORDER BY revenue DESC"
    },
    {
        "q": "RS 매출 현황",
        "sql": "SELECT so.part_number, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id WHERE v.vendor_name='RS' GROUP BY so.part_number ORDER BY revenue DESC"
    },
    {
        "q": "TI 매출 현황",
        "sql": "SELECT so.part_number, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id WHERE v.vendor_name='TI' GROUP BY so.part_number ORDER BY revenue DESC"
    },
    {
        "q": "ST 매출 현황",
        "sql": "SELECT so.part_number, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id WHERE v.vendor_name='ST' GROUP BY so.part_number ORDER BY revenue DESC"
    },
    {
        "q": "ROHM 매출 현황",
        "sql": "SELECT so.part_number, SUM(so.sale_quantity) AS qty, SUM(so.sale_quantity * so.actual_selling_price) AS revenue FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id WHERE v.vendor_name='ROHM' GROUP BY so.part_number ORDER BY revenue DESC"
    },
    {
        "q": "최근 6개월 거래 없는 고객사",
        "sql": "SELECT v.vendor_name FROM vendors v WHERE v.vendor_id NOT IN (SELECT DISTINCT vendor_id FROM sales_orders WHERE sale_date >= CURRENT_DATE - INTERVAL '6 months') ORDER BY v.vendor_name"
    },
    {
        "q": "이번달 매입 총액",
        "sql": "SELECT SUM(purchase_quantity * actual_unit_cost) AS total_purchase FROM purchase_orders WHERE DATE_TRUNC('month', purchase_date)=DATE_TRUNC('month', CURRENT_DATE)"
    },
    {
        "q": "올해 매입 총액",
        "sql": "SELECT SUM(purchase_quantity * actual_unit_cost) AS total_purchase FROM purchase_orders WHERE EXTRACT(YEAR FROM purchase_date)=EXTRACT(YEAR FROM CURRENT_DATE)"
    },
    {
        "q": "2024년 월별 매입 추이",
        "sql": "SELECT DATE_TRUNC('month', purchase_date) AS month, SUM(purchase_quantity * actual_unit_cost) AS purchase_amount FROM purchase_orders WHERE EXTRACT(YEAR FROM purchase_date)=2024 GROUP BY month ORDER BY month"
    },
    {
        "q": "매입 많은 제조사 탑 5",
        "sql": "SELECT m.name, SUM(po.purchase_quantity) AS total_qty, SUM(po.purchase_quantity * po.actual_unit_cost) AS total_amount FROM purchase_orders po JOIN manufacturers m ON po.manufacturer_id=m.manufacturer_id GROUP BY m.name ORDER BY total_amount DESC LIMIT 5"
    },
    {
        "q": "PANASONIC 납품 현황",
        "sql": "SELECT po.part_number, p.description, SUM(po.purchase_quantity) AS qty FROM purchase_orders po JOIN manufacturers m ON po.manufacturer_id=m.manufacturer_id JOIN products p ON po.part_number=p.part_number WHERE m.name='PANASONIC' GROUP BY po.part_number, p.description ORDER BY qty DESC"
    },
    {
        "q": "INTEL 납품 현황",
        "sql": "SELECT po.part_number, SUM(po.purchase_quantity) AS qty FROM purchase_orders po JOIN manufacturers m ON po.manufacturer_id=m.manufacturer_id WHERE m.name IN ('INTEL','INETL') GROUP BY po.part_number ORDER BY qty DESC"
    },
    {
        "q": "BROADCOM 납품 현황",
        "sql": "SELECT po.part_number, SUM(po.purchase_quantity) AS qty FROM purchase_orders po JOIN manufacturers m ON po.manufacturer_id=m.manufacturer_id WHERE m.name IN ('BROADCOM','BROADCO','BROMDCOM','BRPADCOM') GROUP BY po.part_number ORDER BY qty DESC"
    },
    {
        "q": "제조사별 납품 현황 전체",
        "sql": "SELECT m.name, SUM(po.purchase_quantity) AS total_qty, SUM(po.purchase_quantity * po.actual_unit_cost) AS total_amount FROM purchase_orders po JOIN manufacturers m ON po.manufacturer_id=m.manufacturer_id GROUP BY m.name ORDER BY total_amount DESC"
    },
    {
        "q": "최근 6개월 거래 없는 제조사",
        "sql": "SELECT m.name FROM manufacturers m WHERE m.manufacturer_id NOT IN (SELECT DISTINCT manufacturer_id FROM purchase_orders WHERE purchase_date >= CURRENT_DATE - INTERVAL '6 months') ORDER BY m.name"
    },
    {
        "q": "마진율 높은 제품 상위 10개",
        "sql": "SELECT p.part_number, p.description, ROUND((p.std_selling_price - p.std_unit_cost)/p.std_unit_cost*100, 2) AS margin_pct FROM products p WHERE p.std_unit_cost > 0 ORDER BY margin_pct DESC LIMIT 10"
    },
    {
        "q": "이번달 매출 총이익",
        "sql": "SELECT SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost)) AS gross_profit FROM sales_orders so JOIN products p ON so.part_number=p.part_number WHERE DATE_TRUNC('month', so.sale_date)=DATE_TRUNC('month', CURRENT_DATE)"
    },
    {
        "q": "올해 매출 총이익",
        "sql": "SELECT SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost)) AS gross_profit FROM sales_orders so JOIN products p ON so.part_number=p.part_number WHERE EXTRACT(YEAR FROM so.sale_date)=EXTRACT(YEAR FROM CURRENT_DATE)"
    },
    {
        "q": "품목별 수익성 분석",
        "sql": "SELECT so.part_number, p.description, SUM(so.sale_quantity * so.actual_selling_price) AS revenue, SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost)) AS profit FROM sales_orders so JOIN products p ON so.part_number=p.part_number GROUP BY so.part_number, p.description ORDER BY profit DESC LIMIT 20"
    },
    {
        "q": "고객사별 수익성 분석",
        "sql": "SELECT v.vendor_name, SUM(so.sale_quantity * so.actual_selling_price) AS revenue, SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost)) AS profit FROM sales_orders so JOIN vendors v ON so.vendor_id=v.vendor_id JOIN products p ON so.part_number=p.part_number GROUP BY v.vendor_name ORDER BY profit DESC"
    },
    {
        "q": "실제 매입단가 vs 표준단가 비교",
        "sql": "SELECT po.part_number, p.std_unit_cost, ROUND(AVG(po.actual_unit_cost),2) AS avg_actual, ROUND(AVG(po.actual_unit_cost)-p.std_unit_cost,2) AS diff FROM purchase_orders po JOIN products p ON po.part_number=p.part_number GROUP BY po.part_number, p.std_unit_cost ORDER BY diff DESC LIMIT 20"
    },
    {
        "q": "재고회전율 계산",
        "sql": "SELECT cp.part_number, p.description, COALESCE(SUM(so.sale_quantity),0) AS sold_qty, cp.current_quantity, CASE WHEN cp.current_quantity>0 THEN ROUND(COALESCE(SUM(so.sale_quantity),0)::NUMERIC/cp.current_quantity,2) ELSE NULL END AS turnover FROM current_products cp JOIN products p ON cp.part_number=p.part_number LEFT JOIN sales_orders so ON cp.part_number=so.part_number GROUP BY cp.part_number, p.description, cp.current_quantity ORDER BY turnover DESC NULLS LAST LIMIT 20"
    },
    {
        "q": "판매 느린 품목",
        "sql": "SELECT cp.part_number, p.description, cp.current_quantity, COALESCE(SUM(so.sale_quantity),0) AS sold_90days FROM current_products cp JOIN products p ON cp.part_number=p.part_number LEFT JOIN sales_orders so ON cp.part_number=so.part_number AND so.sale_date>=CURRENT_DATE-INTERVAL '90 days' GROUP BY cp.part_number, p.description, cp.current_quantity HAVING cp.current_quantity>0 ORDER BY COALESCE(SUM(so.sale_quantity),0)::NUMERIC/cp.current_quantity ASC LIMIT 20"
    },
    {
        "q": "ABC 분석",
        "sql": "WITH sr AS (SELECT part_number, SUM(sale_quantity*actual_selling_price) AS rev, SUM(SUM(sale_quantity*actual_selling_price)) OVER() AS total FROM sales_orders GROUP BY part_number), cum AS (SELECT part_number, rev, SUM(rev/total*100) OVER(ORDER BY rev DESC) AS cum_pct FROM sr) SELECT part_number, ROUND(rev,0) AS revenue, ROUND(cum_pct,1) AS cum_pct, CASE WHEN cum_pct<=80 THEN 'A' WHEN cum_pct<=95 THEN 'B' ELSE 'C' END AS grade FROM cum ORDER BY rev DESC"
    },
    {
        "q": "2024년 1분기 매출액",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date) = 2024 AND EXTRACT(QUARTER FROM sale_date) = 1"
    },
    {
        "q": "품번이 80-CBR로 시작하는 부품 재고",
        "sql": "SELECT cp.part_number, cp.current_quantity FROM current_products cp WHERE cp.part_number LIKE '80-CBR%'"
    },
    {
        "q": "이번 달 평균 판매 단가(ASP)",
        "sql": "SELECT ROUND(SUM(sale_quantity * actual_selling_price) / SUM(sale_quantity), 0) AS asp FROM sales_orders WHERE DATE_TRUNC('month', sale_date) = DATE_TRUNC('month', CURRENT_DATE)"
    },
    {
        "q": "초기재고와 현재고 차이가 가장 큰 제품",
        "sql": """WITH inventory_diff AS (
    SELECT cp.part_number, p.description, ii.initial_quantity, cp.current_quantity,
           (cp.current_quantity - ii.initial_quantity) AS diff,
           ABS(cp.current_quantity - ii.initial_quantity) AS abs_diff
    FROM current_products cp
    JOIN initial_inventory ii ON cp.part_number = ii.part_number
    JOIN products p ON cp.part_number = p.part_number
)
SELECT part_number, description, initial_quantity, current_quantity, diff
FROM inventory_diff ORDER BY abs_diff DESC LIMIT 1"""
    },
    {
        "q": "초기재고 대비 현재고 변동량 상위 10개",
        "sql": """WITH inventory_diff AS (
    SELECT cp.part_number, p.description, ii.initial_quantity, cp.current_quantity,
           (cp.current_quantity - ii.initial_quantity) AS diff,
           ABS(cp.current_quantity - ii.initial_quantity) AS abs_diff
    FROM current_products cp
    JOIN initial_inventory ii ON cp.part_number = ii.part_number
    JOIN products p ON cp.part_number = p.part_number
)
SELECT part_number, description, initial_quantity, current_quantity, diff
FROM inventory_diff ORDER BY abs_diff DESC LIMIT 10"""
    },
    {
        "q": "초기재고보다 현재고가 많이 줄어든 제품",
        "sql": """WITH inventory_diff AS (
    SELECT cp.part_number, p.description, ii.initial_quantity, cp.current_quantity,
           (cp.current_quantity - ii.initial_quantity) AS diff
    FROM current_products cp
    JOIN initial_inventory ii ON cp.part_number = ii.part_number
    JOIN products p ON cp.part_number = p.part_number
)
SELECT part_number, description, initial_quantity, current_quantity, diff
FROM inventory_diff WHERE diff < 0 ORDER BY diff ASC LIMIT 10"""
    },
    {
        "q": "카테고리별 초기재고 vs 현재고 비교",
        "sql": """WITH inventory_diff AS (
    SELECT p.description AS category,
           SUM(ii.initial_quantity) AS total_initial,
           SUM(cp.current_quantity) AS total_current,
           SUM(cp.current_quantity - ii.initial_quantity) AS total_diff
    FROM current_products cp
    JOIN initial_inventory ii ON cp.part_number = ii.part_number
    JOIN products p ON cp.part_number = p.part_number
    GROUP BY p.description
)
SELECT category, total_initial, total_current, total_diff
FROM inventory_diff ORDER BY ABS(total_diff) DESC"""
    },
    {
        "q": "초기재고 대비 현재고 감소율이 가장 높은 제품",
        "sql": """WITH inventory_diff AS (
    SELECT cp.part_number, p.description, ii.initial_quantity, cp.current_quantity,
           ROUND((ii.initial_quantity - cp.current_quantity)::NUMERIC
                 / NULLIF(ii.initial_quantity,0) * 100, 1) AS decrease_pct
    FROM current_products cp
    JOIN initial_inventory ii ON cp.part_number = ii.part_number
    JOIN products p ON cp.part_number = p.part_number
    WHERE ii.initial_quantity > 0
)
SELECT part_number, description, initial_quantity, current_quantity, decrease_pct
FROM inventory_diff WHERE decrease_pct > 0 ORDER BY decrease_pct DESC LIMIT 10"""
    },
    {
        "q": "특정 부품의 총 구매량과 총 판매량 조회",
        "sql": "SELECT (SELECT SUM(purchase_quantity) FROM purchase_orders WHERE part_number = 'CYP15G0401DXB-BGXI') AS total_purchase_quantity, (SELECT SUM(sale_quantity) FROM sales_orders WHERE part_number = 'CYP15G0401DXB-BGXI') AS total_sale_quantity"
    },
    {
        "q": "ABC-123 부품의 누적 판매량과 누적 구매량은?",
        "sql": "SELECT (SELECT SUM(purchase_quantity) FROM purchase_orders WHERE part_number = 'ABC-123') AS total_purchase_quantity, (SELECT SUM(sale_quantity) FROM sales_orders WHERE part_number = 'ABC-123') AS total_sale_quantity"
    },
    {
        "q": "XYZ-900의 총 구매수량과 총 판매수량을 모두 보여줘 (없으면 0)",
        "sql": "SELECT COALESCE((SELECT SUM(purchase_quantity) FROM purchase_orders WHERE part_number = 'XYZ-900'), 0) AS total_purchase_quantity, COALESCE((SELECT SUM(sale_quantity) FROM sales_orders WHERE part_number = 'XYZ-900'), 0) AS total_sale_quantity"
    },
    {
        "q": "LMN-777 부품의 최근 1년간 총 구매량과 판매량",
        "sql": "SELECT (SELECT SUM(purchase_quantity) FROM purchase_orders WHERE part_number = 'LMN-777' AND purchase_date >= CURRENT_DATE - INTERVAL '1 year') AS total_purchase_quantity, (SELECT SUM(sale_quantity) FROM sales_orders WHERE part_number = 'LMN-777' AND sale_date >= CURRENT_DATE - INTERVAL '1 year') AS total_sale_quantity"
    },
    {
        "q": "현재고와 기초재고 차이가 가장 큰 제품을 가장 많이 사간 구매사와 차이가 가장 적은 제품을 가장 많이 들여온 제조사",
        "sql": """WITH inventory_diff AS (
    SELECT cp.part_number, ABS(cp.current_quantity - ii.initial_quantity) AS abs_diff
    FROM current_products cp
    JOIN initial_inventory ii ON cp.part_number = ii.part_number
),
max_part AS (
    SELECT part_number FROM inventory_diff ORDER BY abs_diff DESC LIMIT 1
),
min_part AS (
    SELECT part_number FROM inventory_diff ORDER BY abs_diff ASC LIMIT 1
),
top_vendor AS (
    SELECT v.vendor_name, SUM(so.sale_quantity) AS qty
    FROM sales_orders so
    JOIN vendors v ON so.vendor_id = v.vendor_id
    WHERE so.part_number = (SELECT part_number FROM max_part)
    GROUP BY v.vendor_name ORDER BY qty DESC LIMIT 1
),
top_manufacturer AS (
    SELECT m.name, SUM(po.purchase_quantity) AS qty
    FROM purchase_orders po
    JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
    WHERE po.part_number = (SELECT part_number FROM min_part)
    GROUP BY m.name ORDER BY qty DESC LIMIT 1
)
SELECT
    (SELECT part_number FROM max_part)   AS 차이최대_제품,
    (SELECT vendor_name FROM top_vendor) AS 가장많이_구매한_고객사,
    (SELECT part_number FROM min_part)   AS 차이최소_제품,
    (SELECT name FROM top_manufacturer)  AS 가장많이_들여온_제조사"""
    },
    {
        "q": "매출이 가장 높은 고객사와 매입이 가장 많은 제조사 동시에 알려줘",
        "sql": """WITH top_vendor AS (
    SELECT v.vendor_name, SUM(so.sale_quantity * so.actual_selling_price)::BIGINT AS total_revenue
    FROM sales_orders so
    JOIN vendors v ON so.vendor_id = v.vendor_id
    GROUP BY v.vendor_name ORDER BY total_revenue DESC LIMIT 1
),
top_manufacturer AS (
    SELECT m.name, SUM(po.purchase_quantity)::BIGINT AS total_qty
    FROM purchase_orders po
    JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
    GROUP BY m.name ORDER BY total_qty DESC LIMIT 1
)
SELECT
    (SELECT vendor_name FROM top_vendor)      AS 매출1위_고객사,
    (SELECT total_revenue FROM top_vendor)    AS 총매출액,
    (SELECT name FROM top_manufacturer)       AS 매입1위_제조사,
    (SELECT total_qty FROM top_manufacturer)  AS 총매입수량"""
    },
    {
        "q": "카테고리 중 매출 가장 높은 것과 가장 낮은 것 둘 다 보여줘",
        "sql": """WITH category_sales AS (
    SELECT p.description, SUM(so.sale_quantity * so.actual_selling_price)::BIGINT AS total_revenue
    FROM sales_orders so
    JOIN products p ON so.part_number = p.part_number
    GROUP BY p.description
)
SELECT
    MAX(description) FILTER (WHERE total_revenue = (SELECT MAX(total_revenue) FROM category_sales)) AS 매출최고_카테고리,
    MAX(total_revenue) FILTER (WHERE total_revenue = (SELECT MAX(total_revenue) FROM category_sales)) AS 최고_매출액,
    MAX(description) FILTER (WHERE total_revenue = (SELECT MIN(total_revenue) FROM category_sales)) AS 매출최저_카테고리,
    MIN(total_revenue) FILTER (WHERE total_revenue = (SELECT MIN(total_revenue) FROM category_sales)) AS 최저_매출액
FROM category_sales"""
    },
    {
        "q": "EP1K50FC256-1 가장 많이 사간 고객사와 가장 많이 납품한 제조사",
        "sql": """WITH top_vendor AS (
    SELECT v.vendor_name, SUM(so.sale_quantity)::BIGINT AS qty
    FROM sales_orders so
    JOIN vendors v ON so.vendor_id = v.vendor_id
    WHERE so.part_number = 'EP1K50FC256-1'
    GROUP BY v.vendor_name ORDER BY qty DESC LIMIT 1
),
top_manufacturer AS (
    SELECT m.name, SUM(po.purchase_quantity)::BIGINT AS qty
    FROM purchase_orders po
    JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
    WHERE po.part_number = 'EP1K50FC256-1'
    GROUP BY m.name ORDER BY qty DESC LIMIT 1
)
SELECT
    (SELECT vendor_name FROM top_vendor)     AS 최다구매_고객사,
    (SELECT qty FROM top_vendor)             AS 구매수량,
    (SELECT name FROM top_manufacturer)      AS 최다납품_제조사,
    (SELECT qty FROM top_manufacturer)       AS 납품수량"""
    },
    {
        "q": "기초재고가 가장 많은 5개 제품 중 현재 재고가 2번째로 많은 제품의 제조사와 판매사",
        "sql": """WITH top_initial_5 AS (
    SELECT
        p.part_number,
        p.description,
        ii.initial_quantity,
        cp.current_quantity
    FROM products p
    JOIN initial_inventory ii
        ON p.part_number = ii.part_number
    JOIN current_products cp
        ON p.part_number = cp.part_number
    ORDER BY ii.initial_quantity DESC
    LIMIT 5
),
target_product AS (
    SELECT *
    FROM top_initial_5
    ORDER BY current_quantity DESC
    OFFSET 1
    LIMIT 1
)
SELECT
    t.part_number,
    t.description,
    t.initial_quantity AS "기초재고",
    t.current_quantity AS "현재고",
    (
        SELECT m.name
        FROM purchase_orders po
        JOIN manufacturers m
            ON po.manufacturer_id = m.manufacturer_id
        WHERE po.part_number = t.part_number
        GROUP BY m.name
        ORDER BY SUM(po.purchase_quantity) DESC
        LIMIT 1
    ) AS "주요 제조사",
    (
        SELECT v.vendor_name
        FROM sales_orders so
        JOIN vendors v
            ON so.vendor_id = v.vendor_id
        WHERE so.part_number = t.part_number
        GROUP BY v.vendor_name
        ORDER BY SUM(so.sale_quantity) DESC
        LIMIT 1
    ) AS "주요 판매사"
FROM target_product t"""
    },
    {
        "q": "올해 vs 작년 월별 매출 YoY 증감률",
        "sql": """WITH monthly AS (
    SELECT EXTRACT(YEAR FROM sale_date)::INT AS yr,
           EXTRACT(MONTH FROM sale_date)::INT AS mn,
           SUM(sale_quantity * actual_selling_price) AS rev
    FROM sales_orders
    WHERE EXTRACT(YEAR FROM sale_date) >= EXTRACT(YEAR FROM CURRENT_DATE) - 1
    GROUP BY yr, mn
)
SELECT cur.mn AS month,
       cur.rev AS 올해매출,
       prev.rev AS 작년매출,
       ROUND((cur.rev - prev.rev) / NULLIF(prev.rev, 0) * 100, 1) AS yoy_pct
FROM monthly cur
JOIN monthly prev ON cur.mn = prev.mn
     AND cur.yr = prev.yr + 1
ORDER BY cur.mn"""
    },
    {
        "q": "최근 6개월 전월대비 매출 증감률",
        "sql": """WITH monthly AS (
    SELECT DATE_TRUNC('month', sale_date) AS month,
           SUM(sale_quantity * actual_selling_price) AS rev
    FROM sales_orders
    WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '6 months'
    GROUP BY month
)
SELECT month, rev,
       LAG(rev) OVER (ORDER BY month) AS prev_rev,
       ROUND((rev - LAG(rev) OVER (ORDER BY month))
             / NULLIF(LAG(rev) OVER (ORDER BY month), 0) * 100, 1) AS mom_pct
FROM monthly ORDER BY month"""
    },
    {
        "q": "2024년 상반기 매출",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date) = 2024 AND EXTRACT(MONTH FROM sale_date) BETWEEN 1 AND 6"
    },
    {
        "q": "2024년 하반기 매입",
        "sql": "SELECT SUM(purchase_quantity * actual_unit_cost) AS purchase_amount FROM purchase_orders WHERE EXTRACT(YEAR FROM purchase_date) = 2024 AND EXTRACT(MONTH FROM purchase_date) BETWEEN 7 AND 12"
    },
    {
        "q": "올해 상반기 vs 하반기 매출 비교",
        "sql": """SELECT
    CASE WHEN EXTRACT(MONTH FROM sale_date) BETWEEN 1 AND 6 THEN '상반기' ELSE '하반기' END AS half,
    SUM(sale_quantity * actual_selling_price) AS revenue
FROM sales_orders
WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY half ORDER BY half"""
    },
    {
        "q": "올해 IC 카테고리 매출",
        "sql": """SELECT SUM(so.sale_quantity * so.actual_selling_price) AS revenue
FROM sales_orders so
JOIN products p ON so.part_number = p.part_number
WHERE p.description = 'IC'
  AND EXTRACT(YEAR FROM so.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)"""
    },
    {
        "q": "2024년 카테고리별 분기별 매출",
        "sql": """SELECT p.description AS category,
       EXTRACT(QUARTER FROM so.sale_date)::INT AS quarter,
       SUM(so.sale_quantity * so.actual_selling_price) AS revenue
FROM sales_orders so
JOIN products p ON so.part_number = p.part_number
WHERE EXTRACT(YEAR FROM so.sale_date) = 2024
GROUP BY category, quarter
ORDER BY category, quarter"""
    },
    {
        "q": "Digikey의 2024년 월별 매출 추이",
        "sql": """SELECT DATE_TRUNC('month', so.sale_date) AS month,
       SUM(so.sale_quantity * so.actual_selling_price) AS revenue
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
WHERE v.vendor_name = 'Digikey'
  AND EXTRACT(YEAR FROM so.sale_date) = 2024
GROUP BY month ORDER BY month"""
    },
    {
        "q": "PANASONIC에서 올해 월별 매입 추이",
        "sql": """SELECT DATE_TRUNC('month', po.purchase_date) AS month,
       SUM(po.purchase_quantity * po.actual_unit_cost) AS purchase_amount
FROM purchase_orders po
JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
WHERE m.name = 'PANASONIC'
  AND EXTRACT(YEAR FROM po.purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY month ORDER BY month"""
    },
    {
        "q": "2024년 월별 누적 매출",
        "sql": """SELECT month, revenue,
       SUM(revenue) OVER (ORDER BY month) AS cumulative_revenue
FROM (
    SELECT DATE_TRUNC('month', sale_date) AS month,
           SUM(sale_quantity * actual_selling_price) AS revenue
    FROM sales_orders
    WHERE EXTRACT(YEAR FROM sale_date) = 2024
    GROUP BY month
) sub ORDER BY month"""
    },
    {
        "q": "월 매출 1억 이상인 달",
        "sql": """SELECT DATE_TRUNC('month', sale_date) AS month,
       SUM(sale_quantity * actual_selling_price) AS revenue
FROM sales_orders
GROUP BY month
HAVING SUM(sale_quantity * actual_selling_price) >= 100000000
ORDER BY month"""
    },
    {
        "q": "연간 매입 1000건 이상인 제조사",
        "sql": """SELECT m.name, COUNT(*) AS order_count,
       SUM(po.purchase_quantity * po.actual_unit_cost) AS total_amount
FROM purchase_orders po
JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
WHERE EXTRACT(YEAR FROM po.purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY m.name
HAVING COUNT(*) >= 1000
ORDER BY total_amount DESC"""
    },
    {
        "q": "고객사별 매출 점유율",
        "sql": """SELECT v.vendor_name,
       SUM(so.sale_quantity * so.actual_selling_price) AS revenue,
       ROUND(SUM(so.sale_quantity * so.actual_selling_price)
             / SUM(SUM(so.sale_quantity * so.actual_selling_price)) OVER () * 100, 1) AS share_pct
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
GROUP BY v.vendor_name
ORDER BY revenue DESC"""
    },
    {
        "q": "제조사별 매입 점유율",
        "sql": """SELECT m.name,
       SUM(po.purchase_quantity * po.actual_unit_cost) AS amount,
       ROUND(SUM(po.purchase_quantity * po.actual_unit_cost)
             / SUM(SUM(po.purchase_quantity * po.actual_unit_cost)) OVER () * 100, 1) AS share_pct
FROM purchase_orders po
JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
GROUP BY m.name
ORDER BY amount DESC"""
    },
    {
        "q": "월별 평균판매단가 추이",
        "sql": """SELECT DATE_TRUNC('month', sale_date) AS month,
       ROUND(SUM(sale_quantity * actual_selling_price)::NUMERIC
             / NULLIF(SUM(sale_quantity), 0), 2) AS asp
FROM sales_orders
GROUP BY month ORDER BY month"""
    },
    {
        "q": "월별 평균매입단가 추이",
        "sql": """SELECT DATE_TRUNC('month', purchase_date) AS month,
       ROUND(SUM(purchase_quantity * actual_unit_cost)::NUMERIC
             / NULLIF(SUM(purchase_quantity), 0), 2) AS avg_purchase_price
FROM purchase_orders
GROUP BY month ORDER BY month"""
    },
    {
        "q": "카테고리별 재고 자산가치",
        "sql": """SELECT p.description AS category,
       SUM(cp.current_quantity) AS total_qty,
       SUM(cp.current_quantity * p.std_unit_cost) AS stock_value
FROM current_products cp
JOIN products p ON cp.part_number = p.part_number
GROUP BY p.description
ORDER BY stock_value DESC"""
    },
    {
        "q": "재고 금액 상위 10개 품목",
        "sql": """SELECT cp.part_number, p.description,
       cp.current_quantity,
       p.std_unit_cost,
       (cp.current_quantity * p.std_unit_cost) AS stock_value
FROM current_products cp
JOIN products p ON cp.part_number = p.part_number
ORDER BY stock_value DESC LIMIT 10"""
    },
    {
        "q": "재고일수 계산 (평균 일일 판매량 기준)",
        "sql": """WITH daily_avg AS (
    SELECT part_number,
           SUM(sale_quantity)::NUMERIC / NULLIF(COUNT(DISTINCT sale_date), 0) AS avg_daily_sales
    FROM sales_orders
    WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY part_number
)
SELECT cp.part_number, p.description,
       cp.current_quantity,
       ROUND(d.avg_daily_sales, 1) AS avg_daily_sales,
       CASE WHEN d.avg_daily_sales > 0
            THEN ROUND(cp.current_quantity / d.avg_daily_sales, 0)
            ELSE NULL END AS days_of_stock
FROM current_products cp
JOIN products p ON cp.part_number = p.part_number
LEFT JOIN daily_avg d ON cp.part_number = d.part_number
WHERE cp.current_quantity > 0
ORDER BY days_of_stock ASC NULLS LAST LIMIT 20"""
    },
    {
        "q": "올해 월별 매출총이익 추이",
        "sql": """SELECT DATE_TRUNC('month', so.sale_date) AS month,
       SUM(so.sale_quantity * so.actual_selling_price) AS revenue,
       SUM(so.sale_quantity * p.std_unit_cost) AS cost,
       SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost)) AS gross_profit
FROM sales_orders so
JOIN products p ON so.part_number = p.part_number
WHERE EXTRACT(YEAR FROM so.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY month ORDER BY month"""
    },
    {
        "q": "고객사별 평균 마진율",
        "sql": """SELECT v.vendor_name,
       SUM(so.sale_quantity * so.actual_selling_price) AS revenue,
       SUM(so.sale_quantity * p.std_unit_cost) AS cost,
       ROUND(SUM(so.sale_quantity * (so.actual_selling_price - p.std_unit_cost))::NUMERIC
             / NULLIF(SUM(so.sale_quantity * so.actual_selling_price), 0) * 100, 1) AS margin_pct
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
JOIN products p ON so.part_number = p.part_number
GROUP BY v.vendor_name
ORDER BY margin_pct DESC"""
    },
    {
        "q": "올해 신규 거래 고객사 (작년에 거래 없던)",
        "sql": """SELECT DISTINCT v.vendor_name
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
WHERE EXTRACT(YEAR FROM so.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
  AND so.vendor_id NOT IN (
      SELECT DISTINCT vendor_id FROM sales_orders
      WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
  )
ORDER BY v.vendor_name"""
    },
    {
        "q": "작년 거래했지만 올해 거래 없는 고객사",
        "sql": """SELECT DISTINCT v.vendor_name
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
WHERE EXTRACT(YEAR FROM so.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
  AND so.vendor_id NOT IN (
      SELECT DISTINCT vendor_id FROM sales_orders
      WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
  )
ORDER BY v.vendor_name"""
    },
    {
        "q": "2024년 3월 매출",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE sale_date >= '2024-03-01' AND sale_date < '2024-04-01'"
    },
    {
        "q": "2024년 3월~6월 매출",
        "sql": "SELECT SUM(sale_quantity * actual_selling_price) AS revenue FROM sales_orders WHERE sale_date >= '2024-03-01' AND sale_date < '2024-07-01'"
    },
    {
        "q": "올해 거래한 고객사 수",
        "sql": "SELECT COUNT(DISTINCT vendor_id) AS vendor_count FROM sales_orders WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
    },
    {
        "q": "올해 거래한 제조사 수",
        "sql": "SELECT COUNT(DISTINCT manufacturer_id) AS mfr_count FROM purchase_orders WHERE EXTRACT(YEAR FROM purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
    },
    {
        "q": "판매된 적 있는 품목 수",
        "sql": "SELECT COUNT(DISTINCT part_number) AS product_count FROM sales_orders"
    },
    {
        "q": "고객사별 매출 순위",
        "sql": """SELECT v.vendor_name,
       SUM(so.sale_quantity * so.actual_selling_price) AS revenue,
       RANK() OVER (ORDER BY SUM(so.sale_quantity * so.actual_selling_price) DESC) AS rank
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
GROUP BY v.vendor_name
ORDER BY rank"""
    },
    {
        "q": "요일별 평균 판매량",
        "sql": """SELECT TO_CHAR(sale_date, 'Day') AS day_of_week,
       EXTRACT(DOW FROM sale_date) AS dow,
       ROUND(AVG(sale_quantity), 1) AS avg_qty,
       COUNT(*) AS order_count
FROM sales_orders
GROUP BY day_of_week, dow
ORDER BY dow"""
    },
    {
        "q": "EP1K50FC256-1 최근 판매이력 10건",
        "sql": """SELECT so.order_id, so.sale_date, v.vendor_name,
       so.sale_quantity, so.actual_selling_price
FROM sales_orders so
JOIN vendors v ON so.vendor_id = v.vendor_id
WHERE so.part_number = 'EP1K50FC256-1'
ORDER BY so.sale_date DESC LIMIT 10"""
    },
    {
        "q": "EP1K50FC256-1 최근 매입이력 10건",
        "sql": """SELECT po.purchase_id, po.purchase_date, m.name AS manufacturer,
       po.purchase_quantity, po.actual_unit_cost
FROM purchase_orders po
JOIN manufacturers m ON po.manufacturer_id = m.manufacturer_id
WHERE po.part_number = 'EP1K50FC256-1'
ORDER BY po.purchase_date DESC LIMIT 10"""
    },
    {
        "q": "올해 전체 요약 (매출/매입/이익)",
        "sql": """SELECT
    (SELECT SUM(sale_quantity * actual_selling_price) FROM sales_orders
     WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)) AS 총매출,
    (SELECT SUM(purchase_quantity * actual_unit_cost) FROM purchase_orders
     WHERE EXTRACT(YEAR FROM purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)) AS 총매입,
    (SELECT SUM(sale_quantity * actual_selling_price) FROM sales_orders
     WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE))
    -
    (SELECT SUM(purchase_quantity * actual_unit_cost) FROM purchase_orders
     WHERE EXTRACT(YEAR FROM purchase_date) = EXTRACT(YEAR FROM CURRENT_DATE)) AS 매출매입차이"""
    },
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
]

# ── 4. 테이블-컬럼 Rich 문장 (스키마 설명) ── RAG 강화 버전 ──────────────────
TABLE_SCHEMA_DATA = [
    {
        "doc": (
            "current_products 테이블은 현재 보유 중인 실시간 재고 수량을 저장하는 현재 재고 테이블이다. "
            "지금 재고가 얼마인지 조회하려면 이 테이블을 사용한다. "
            "current_products 테이블: 모든 입출고 이력을 합산한 실시간 재고 현황 스냅샷. "
            "재고 수량은 '초기재고(initial_inventory) + 총매입(purchase_orders) - 총판매(sales_orders)'로 계산된 최종 결과물이다. "
            "컬럼: part_number(품번 VARCHAR PK, products 테이블 참조), "
            "description(부품 카테고리코드: IC, FET/TR, C_CHIP, CAP, R_CHIP, RES 등), "
            "current_quantity(현재 보유 재고수량 INTEGER, 실시간 합산값), "
            "last_updated(마지막 재고 계산·갱신 일자 DATE). "
            "주의사항: 이 테이블은 항상 최신 스냅샷이므로 날짜 필터(WHERE last_updated = ...)를 걸지 않고 전체 조회해야 한다. "
            "재고가 0 이하이면 품절·결품 상태를 의미한다. "
            "키워드: 재고 현황 지금 현재 보유 수량 품절 결품 잔량 남은 수량 스톡 stock 가용재고"
        ),
        "meta": {"table": "current_products", "type": "table_schema"}
    },
    {
        "doc": (
            "products 테이블: 회사가 취급하는 300종 전자부품의 핵심 마스터 정보를 관리한다. 날짜 컬럼이 없으므로 시계열 필터 불가. "
            "컬럼: part_number(품번 VARCHAR PK, 예: '80-CBR04C...'), "
            "description(부품 카테고리코드: IC, FET/TR, C_CHIP, CAP, R_CHIP, RES 등 — 부품 종류 분류용), "
            "std_unit_cost(표준 매입 원가 NUMERIC, 예산 수립·원가 분석의 기준 단가), "
            "std_selling_price(표준 판매 가격 NUMERIC, 시장 고시가·기준 마진율 산출용). "
            "조인: purchase_orders.part_number = products.part_number (매입 이력 연결), "
            "sales_orders.part_number = products.part_number (판매 이력 연결), "
            "initial_inventory.part_number = products.part_number (초기 재고 연결). "
            "활용: 표준단가 대비 실제단가 차이(price variance) 분석, 카테고리별 매출·매입 집계, 마진율(margin) 계산 시 기준 테이블. "
            "마진율 계산식: (std_selling_price - std_unit_cost) / std_selling_price * 100. "
            "키워드: 제품 품목 단가 표준가격 마스터 카테고리 원가 판매가 마진 부품 품번 목록"
        ),
        "meta": {"table": "products", "type": "table_schema"}
    },
    {
        "doc": (
            "sales_orders 테이블은 고객사에게 제품을 판매한 모든 매출·출고·판매 주문 이력을 저장하는 핵심 매출 테이블이다. "
            "매출을 조회하려면 반드시 이 테이블을 사용한다. "
            "고객사별 매출, 제품별 판매량, 기간별 매출액을 계산할 때 사용하는 테이블이다. "
            "sales_orders 테이블: 매출·판매·주문·출고 이력. 약 39,572건. 매주 수요일·금요일 정기 납품 패턴이 반영되어 있다. "
            "컬럼: order_id(주문번호 INTEGER PK, 판매 건별 고유 식별자), "
            "vendor_id(고객사 ID INTEGER FK → vendors.vendor_id JOIN으로 고객사명 조회), "
            "part_number(품번 VARCHAR FK → products.part_number JOIN으로 제품 정보 조회), "
            "sale_quantity(판매·출고 수량 INTEGER, 건당 20~150개 분할 출고), "
            "sale_date(판매·출고일 DATE, 범위 2023-01-04 ~ 2025-12-31), "
            "actual_selling_price(실제 판매 단가 NUMERIC, 거래처별 실거래가 — 표준가와 차이 발생 가능). "
            "매출액 계산: sale_quantity * actual_selling_price. "
            "조인: sales_orders.vendor_id = vendors.vendor_id (고객사명 조회), "
            "sales_orders.part_number = products.part_number (카테고리·표준단가 조회). "
            "활용: 기간별 매출 집계, 고객사별 매출 순위, 제품별 판매 추이, 월별·분기별·연도별 매출 분석, "
            "실판매가 vs 표준판매가 차이 분석, 요일별 출고 패턴 분석. "
            "키워드: 매출 판매 주문 출고 얼마 실적 revenue 매출액 납품 거래 수주 고객 top 순위 랭킹 "
            "매출조회 판매이력 판매내역 얼마 벌었 얼마 팔았 거래내역"
        ),
        "meta": {"table": "sales_orders", "type": "table_schema"}
    },
    {
        "doc": (
            "purchase_orders 테이블은 제조사로부터 제품을 구매한 모든 매입·발주·입고 이력을 저장하는 매입 테이블이다. "
            "매입 금액이나 구매 내역을 조회하려면 이 테이블을 사용한다. "
            "purchase_orders 테이블: 매입·구매·발주·입고 이력. 약 13,615건. 매월 1일·15일 배치 발주 패턴이 반영되어 있다. "
            "컬럼: purchase_id(발주번호 INTEGER PK, 구매 건별 고유 식별자), "
            "manufacturer_id(제조사 ID INTEGER FK → manufacturers.manufacturer_id JOIN으로 제조사명 조회), "
            "part_number(품번 VARCHAR FK → products.part_number JOIN으로 제품 정보 조회), "
            "purchase_quantity(매입·입고 수량 INTEGER, 건당 500~1,500개 대량 입고), "
            "purchase_date(매입·입고일 DATE, 범위 2023-01-01 ~ 2025-12-31), "
            "actual_unit_cost(실제 매입 단가 NUMERIC, 시점별 원가 추적 — 표준원가와 차이 발생 가능). "
            "매입액 계산: purchase_quantity * actual_unit_cost. "
            "조인: purchase_orders.manufacturer_id = manufacturers.manufacturer_id (제조사명 조회), "
            "purchase_orders.part_number = products.part_number (카테고리·표준원가 조회). "
            "활용: 기간별 매입 집계, 제조사별 구매 비중, 원가 변동 추이, 월별·분기별 매입 분석, "
            "실매입가 vs 표준매입가 차이(purchase price variance) 분석, 발주 주기 분석. "
            "키워드: 매입 구매 발주 납품 입고 원가 cost 매입액 공급 조달 구매비용 제조사별"
        ),
        "meta": {"table": "purchase_orders", "type": "table_schema"}
    },
    {
        "doc": (
            "vendors 테이블은 제품을 구매하는 고객사(거래처, 판매처, 바이어) 정보를 저장하는 고객사 마스터 테이블이다. "
            "고객사 정보를 조회하려면 이 테이블을 사용한다. "
            "고객사 이름, 거래처 목록, 판매처 정보를 확인할 때 사용하는 테이블이다. "
            "vendors 테이블: 고객사·판매처·거래처·바이어 마스터. 총 29개 업체. "
            "컬럼: vendor_id(INTEGER PK, 고객사 고유 식별자), "
            "vendor_name(VARCHAR, 고객사명, UNIQUE 제약). "
            "주요 고객사 예시: Digikey(디지키), Mouser(마우저), Farnell(파넬), RS Components(알에스), "
            "TI, ST, ROHM(로옴), TOSHIBA(도시바), ON SEMI(온세미), SEOULSEMICON(서울반도체) 등. "
            "조인: sales_orders.vendor_id = vendors.vendor_id (판매 이력에서 고객사명 JOIN). "
            "활용: 고객사별 매출 순위, 고객사별 구매 품목 분석, 주요 거래처 집중도(파레토) 분석, "
            "고객사별 판매 단가 비교, 고객사 이탈·신규 분석. "
            "검색 팁: 고객사명 검색 시 LIKE 또는 ILIKE 사용 권장 (예: WHERE vendor_name ILIKE '%digikey%'). "
            "키워드: 고객사 판매처 거래처 바이어 납품처 유통사 대리점 누구에게 어디에 판매 "
            "고객사정보 고객정보 거래처정보 판매처정보 바이어정보 업체정보 누구에게 판매"
        ),
        "meta": {"table": "vendors", "type": "table_schema"}
    },
    {
        "doc": (
            "manufacturers 테이블: 제조사·공급사·납품처·벤더 마스터. 총 69개 업체. "
            "컬럼: manufacturer_id(INTEGER PK, 제조사 고유 식별자), "
            "name(VARCHAR, 제조사명, UNIQUE 제약으로 중복 등록 방지). "
            "주요 제조사 예시: PANASONIC(파나소닉), INTEL(인텔), BROADCOM(브로드컴), XILINX(자일링스), "
            "MICRON(마이크론), INFINEON(인피니온), MARVELL(마벨), CYPRESS(사이프레스), "
            "RENESAS(르네사스), TEXAS INSTRUMENTS(텍사스인스트루먼트), SAMSUNG(삼성) 등. "
            "오타·별칭 주의: BROADCO→BROADCOM, INETL→INTEL, RENASAS→RENESAS 등 오타 빈발. "
            "조인: purchase_orders.manufacturer_id = manufacturers.manufacturer_id (매입 이력에서 제조사명 JOIN). "
            "활용: 제조사별 매입 비중, 공급처 다변화 분석, 제조사별 납품 단가 추이, 공급 리스크 분석. "
            "검색 팁: 제조사명 검색 시 ILIKE 사용 권장 (예: WHERE name ILIKE '%intel%'). "
            "키워드: 제조사 공급사 납품처 벤더 메이커 브랜드 어디서 구매 공급업체 supplier"
        ),
        "meta": {"table": "manufacturers", "type": "table_schema"}
    },
    {
        "doc": (
            "initial_inventory 테이블: 시스템 운영 시작점(2022-12-31) 기준의 기초 재고 스냅샷. "
            "컬럼: part_number(품번 VARCHAR PK FK → products.part_number), "
            "initial_quantity(기초 재고 수량 INTEGER, 200~800개 사이 무작위 부여), "
            "stock_date(기초 데이터 확정일 DATE, 항상 '2022-12-31' 고정값). "
            "조인: initial_inventory.part_number = products.part_number (제품 마스터 연결). "
            "활용: 재고 변동 추적의 시작점. current_products.current_quantity = "
            "initial_inventory.initial_quantity + SUM(purchase_orders.purchase_quantity) - SUM(sales_orders.sale_quantity) "
            "공식으로 현재 재고 검증 가능. 기초 재고 대비 증감 분석에 활용. "
            "키워드: 초기재고 최초입고 시작재고 기초재고 오프닝 opening stock 기준일 재고"
        ),
        "meta": {"table": "initial_inventory", "type": "table_schema"}
    },
    {
        "doc": (
            "테이블 조인 관계(JOIN Map) 및 ERD 구조: "
            "1) sales_orders.part_number = products.part_number — 판매 이력에 제품 카테고리·표준단가 연결. "
            "2) purchase_orders.part_number = products.part_number — 매입 이력에 제품 카테고리·표준원가 연결. "
            "3) sales_orders.vendor_id = vendors.vendor_id — 판매 이력에 고객사명 연결. "
            "4) purchase_orders.manufacturer_id = manufacturers.manufacturer_id — 매입 이력에 제조사명 연결. "
            "5) initial_inventory.part_number = products.part_number — 초기 재고에 제품 정보 연결. "
            "6) current_products.part_number = products.part_number — 현재 재고에 제품 정보 연결. "
            "관계 유형: products(1) ↔ purchase_orders(N) 일대다, products(1) ↔ sales_orders(N) 일대다, "
            "vendors(1) ↔ sales_orders(N) 일대다, manufacturers(1) ↔ purchase_orders(N) 일대다. "
            "핵심 분석 조인 패턴: "
            "① 매출 분석: sales_orders JOIN products JOIN vendors — 고객사별·카테고리별 매출. "
            "② 매입 분석: purchase_orders JOIN products JOIN manufacturers — 제조사별·카테고리별 매입. "
            "③ 손익 분석: sales_orders + purchase_orders를 products 기준으로 통합 — 품목별 매출-매입 마진. "
            "④ 재고 검증: initial_inventory + purchase_orders - sales_orders = current_products."
        ),
        "meta": {"table": "join_relations", "type": "table_schema"}
    },
    {
        "doc": (
            "비즈니스 용어-SQL 매핑 가이드: "
            "매출액 = SUM(sales_orders.sale_quantity * sales_orders.actual_selling_price). "
            "매입액 = SUM(purchase_orders.purchase_quantity * purchase_orders.actual_unit_cost). "
            "매출총이익(gross profit) = 매출액 - 매입액. "
            "표준마진율 = (products.std_selling_price - products.std_unit_cost) / products.std_selling_price * 100. "
            "실제마진율 = (actual_selling_price - actual_unit_cost) / actual_selling_price * 100 (동일 품번 기준). "
            "판매단가 차이(selling price variance) = actual_selling_price - std_selling_price. "
            "매입단가 차이(purchase price variance) = actual_unit_cost - std_unit_cost. "
            "재고회전율 = 총 판매수량 / 평균재고수량. "
            "현재재고 = current_products.current_quantity (또는 initial_quantity + 총매입수량 - 총판매수량). "
            "월별 집계 시: DATE_TRUNC('month', sale_date) 또는 EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date). "
            "분기별 집계 시: DATE_TRUNC('quarter', sale_date) 또는 EXTRACT(QUARTER FROM sale_date). "
            "연도별 집계 시: DATE_TRUNC('year', sale_date) 또는 EXTRACT(YEAR FROM sale_date). "
            "TOP N 조회 시: ORDER BY ... DESC LIMIT N. "
            "증감률 = (현재값 - 이전값) / 이전값 * 100. "
            "전년대비 증감률(YoY) = (올해값 - 작년값) / 작년값 * 100. "
            "전월대비 증감률(MoM) = (이번달값 - 전월값) / 전월값 * 100. "
            "평균판매단가(ASP) = SUM(sale_quantity * actual_selling_price) / SUM(sale_quantity). "
            "평균매입단가 = SUM(purchase_quantity * actual_unit_cost) / SUM(purchase_quantity). "
            "누적매출 = SUM(매출액) OVER (ORDER BY sale_date). "
            "러닝합계 = SUM(...) OVER (ORDER BY 날짜). "
            "키워드: 매출액 매입액 이익 마진 마진율 손익 수익 profit margin revenue cost 회전율"
        ),
        "meta": {"table": "business_glossary", "type": "table_schema"}
    },
    {
        "doc": (
            "날짜·기간 필터 가이드: "
            "데이터 범위 — purchase_orders: 2023-01-01 ~ 2025-12-31, sales_orders: 2023-01-04 ~ 2025-12-31. "
            "current_products: 날짜 필터 금지, 항상 전체 조회 (last_updated는 참고용). "
            "initial_inventory: stock_date는 항상 2022-12-31 고정, 필터 불필요. "
            "products, vendors, manufacturers: 날짜 컬럼 없음 — 시계열 필터 불가. "
            "'올해'는 CURRENT_DATE 기준 연도. "
            "'작년'은 CURRENT_DATE - 1 year. "
            "'재작년'은 CURRENT_DATE - 2 year. "
            "'이번 달' = DATE_TRUNC('month', CURRENT_DATE). "
            "'최근 3개월' = sale_date >= CURRENT_DATE - INTERVAL '3 months'. "
            "'전월' = sale_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') "
            "AND sale_date < DATE_TRUNC('month', CURRENT_DATE). "
            "'최근 N개월' = sale_date >= CURRENT_DATE - INTERVAL 'N months'. "
            "'최근 N일' = sale_date >= CURRENT_DATE - INTERVAL 'N days'. "
            "'상반기' = EXTRACT(MONTH FROM date) BETWEEN 1 AND 6, '하반기' = BETWEEN 7 AND 12. "
            "'1분기' = Q1(1-3월), '2분기' = Q2(4-6월), '3분기' = Q3(7-9월), '4분기' = Q4(10-12월). "
            "판매 패턴: 매주 수요일·금요일 정기 납품. 매입 패턴: 매월 1일·15일 배치 발주. "
            "키워드: 날짜 기간 월별 분기별 연도별 올해 작년 최근 언제 when 추이 트렌드 trend"
        ),
        "meta": {"table": "date_filter_guide", "type": "table_schema"}
    },
    {
        "doc": (
            "부품 카테고리(description) 분류 가이드: "
            "products.description 및 current_products.description 컬럼에 저장된 카테고리코드 목록. "
            "IC: 집적회로(Integrated Circuit) — CPU, MCU, FPGA, 메모리 등 반도체 칩. "
            "FET/TR: 트랜지스터·FET — MOSFET, IGBT 등 스위칭·증폭 소자. "
            "C_CHIP: 칩 세라믹 콘덴서(MLCC) — 소형 표면실장 커패시터. "
            "CAP: 일반 커패시터(캐패시터) — 전해, 필름, 탄탈 등. "
            "R_CHIP: 칩 저항 — 소형 표면실장 저항기. "
            "RES: 일반 저항(레지스터) — 탄소피막, 금속피막 등. "
            "카테고리별 집계 시: GROUP BY description 또는 WHERE description = 'IC'. "
            "LIKE 패턴: WHERE description LIKE '%CHIP%' (칩 부품만), WHERE description IN ('IC','FET/TR') (반도체류). "
            "키워드: 카테고리 부품종류 IC 반도체 저항 콘덴서 커패시터 칩 분류 타입 type category"
        ),
        "meta": {"table": "category_guide", "type": "table_schema"}
    },
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

