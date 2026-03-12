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
# ── 4. 테이블-컬럼 Rich 문장 (스키마 설명) ── RAG 강화 버전 ──────────────────
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



