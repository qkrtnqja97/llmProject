# app/repositories/dashboard_repository.py
import asyncpg

class DashboardRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_top_sales(self, year: int, top_y: int):
        """특정 연도(year)의 순이익 상위 품목 조회"""
        query = """
            WITH product_revenue AS (
                SELECT part_number, SUM(sale_quantity * actual_selling_price) as total_revenue
                FROM inventory_mgmt.sales_orders
                WHERE extract(year from sale_date) = $1  -- 📍 연도 필터 추가
                GROUP BY part_number
            ),
            product_cost AS (
                SELECT part_number, SUM(purchase_quantity * actual_unit_cost) as total_cost
                FROM inventory_mgmt.purchase_orders
                WHERE extract(year from purchase_date) = $1 -- 📍 연도 필터 추가
                GROUP BY part_number
            )
            SELECT 
                p.part_number AS id,
                p.description AS category,
                COALESCE(r.total_revenue, 0) AS sales_amount,
                COALESCE(c.total_cost, 0) AS purchase_amount,
                (COALESCE(r.total_revenue, 0) - COALESCE(c.total_cost, 0)) AS total_amount
            FROM inventory_mgmt.products p
            LEFT JOIN product_revenue r ON p.part_number = r.part_number
            LEFT JOIN product_cost c ON p.part_number = c.part_number
            WHERE (COALESCE(r.total_revenue, 0) - COALESCE(c.total_cost, 0)) <> 0
            ORDER BY total_amount DESC
            LIMIT $2
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, year, top_y)
            return [
                {
                    "id": r["id"],
                    "category": r["category"],
                    "sales": float(r["sales_amount"]),
                    "purchase": float(r["purchase_amount"]),
                    "amount": float(r["total_amount"]),
                    "name": r["id"]
                } for r in rows
            ]

    async def get_bottom_sales(self, year: int, top_y: int):
        """특정 연도(year)의 순이익 하위 품목 조회"""
        query = """
            WITH product_revenue AS (
                SELECT part_number, SUM(sale_quantity * actual_selling_price) as total_revenue
                FROM inventory_mgmt.sales_orders
                WHERE extract(year from sale_date) = $1  -- 📍 연도 필터 추가
                GROUP BY part_number
            ),
            product_cost AS (
                SELECT part_number, SUM(purchase_quantity * actual_unit_cost) as total_cost
                FROM inventory_mgmt.purchase_orders
                WHERE extract(year from purchase_date) = $1 -- 📍 연도 필터 추가
                GROUP BY part_number
            )
            SELECT 
                p.part_number AS id,
                p.description AS category,
                COALESCE(r.total_revenue, 0) AS sales_amount,
                COALESCE(c.total_cost, 0) AS purchase_amount,
                (COALESCE(r.total_revenue, 0) - COALESCE(c.total_cost, 0)) AS total_amount
            FROM inventory_mgmt.products p
            LEFT JOIN product_revenue r ON p.part_number = r.part_number
            LEFT JOIN product_cost c ON p.part_number = c.part_number
            WHERE (COALESCE(r.total_revenue, 0) - COALESCE(c.total_cost, 0)) <> 0
            ORDER BY total_amount ASC
            LIMIT $2
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, year, top_y)
            return [
                {
                    "id": r["id"],
                    "category": r["category"],
                    "sales": float(r["sales_amount"]),
                    "purchase": float(r["purchase_amount"]),
                    "amount": float(r["total_amount"]),
                    "name": r["id"]
                } for r in rows
            ]

    async def get_monthly_profit_loss(self):
        """[분리1: 메인 차트] 시스템 전체의 모든 기간 월별 경영 실적 (필터 없음)"""
        query = """
            WITH monthly_sales AS (
                SELECT to_char(sale_date, 'YYYY-MM') as month,
                       SUM(sale_quantity * actual_selling_price) as s_amount
                FROM inventory_mgmt.sales_orders
                GROUP BY 1
            ),
            monthly_purchase AS (
                SELECT to_char(purchase_date, 'YYYY-MM') as month,
                       SUM(purchase_quantity * actual_unit_cost) as p_amount
                FROM inventory_mgmt.purchase_orders
                GROUP BY 1
            ),
            all_months AS (
                SELECT month FROM monthly_sales
                UNION
                SELECT month FROM monthly_purchase
            )
            SELECT 
                am.month,
                COALESCE(s.s_amount, 0) as sales,
                COALESCE(p.p_amount, 0) as purchase,
                (COALESCE(s.s_amount, 0) - COALESCE(p.p_amount, 0)) as profit
            FROM all_months am
            LEFT JOIN monthly_sales s ON am.month = s.month
            LEFT JOIN monthly_purchase p ON am.month = p.month
            ORDER BY am.month ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def get_product_monthly_trend(self, part_number: str, year: int):
        """[분리2: 상세 차트] 선택한 특정 품목의 특정 연도(12개월) 월별 추이"""
        query = """
            WITH month_series AS (
                SELECT to_char(make_date($2, m, 1), 'YYYY-MM') as month
                FROM generate_series(1, 12) m
            ),
            product_sales AS (
                SELECT to_char(sale_date, 'YYYY-MM') as month,
                       SUM(sale_quantity * actual_selling_price) as s_amount
                FROM inventory_mgmt.sales_orders
                WHERE part_number = $1 AND extract(year from sale_date) = $2
                GROUP BY 1
            ),
            product_purchase AS (
                SELECT to_char(purchase_date, 'YYYY-MM') as month,
                       SUM(purchase_quantity * actual_unit_cost) as p_amount
                FROM inventory_mgmt.purchase_orders
                WHERE part_number = $1 AND extract(year from purchase_date) = $2
                GROUP BY 1
            )
            SELECT 
                ms.month,
                COALESCE(s.s_amount, 0) as sales,
                COALESCE(p.p_amount, 0) as purchase,
                (COALESCE(s.s_amount, 0) - COALESCE(p.p_amount, 0)) as profit
            FROM month_series ms
            LEFT JOIN product_sales s ON ms.month = s.month
            LEFT JOIN product_purchase p ON ms.month = p.month
            ORDER BY ms.month ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, part_number, year)
            return [dict(r) for r in rows]

    async def get_low_inventory(self, threshold: int = 50):
        """재고 부족 현황 조회"""
        query = """
            SELECT 
                COUNT(*) OVER() as total_kind_count,
                cp.part_number as id, 
                p.description as product_name,
                cp.current_quantity as stock
            FROM inventory_mgmt.current_products cp
            JOIN inventory_mgmt.products p ON cp.part_number = p.part_number
            WHERE cp.current_quantity <= $1
            ORDER BY cp.current_quantity ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, threshold)
            if not rows: return {"total_count": 0, "items": []}
            return {
                "total_count": rows[0]["total_kind_count"],
                "items": [{"id": r["id"], "name": r["product_name"], "stock": r["stock"]} for r in rows]
            }

    async def get_weekly_sales_pattern(self):
        """요일별 판매 빈도"""
        query = """
            SELECT to_char(sale_date, 'Dy') as weekday, extract(dow from sale_date) as dow, COUNT(*) as count
            FROM inventory_mgmt.sales_orders
            GROUP BY 1, 2 ORDER BY 2
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query)

    async def get_calendar_events(self):
        """이벤트 조회 (Mock 데이터 포함)"""
        try:
            query = "SELECT '오늘' as date, title, event_type as type FROM users.calendar_events LIMIT 3"
            async with self.pool.acquire() as conn:
                return [dict(r) for r in await conn.fetch(query)]
        except:
            return [
                {"date": "오늘", "title": "재고 실사 점검", "type": "urgent"},
                {"date": "내일", "title": "신규 부품 입고 예정", "type": "normal"}
            ]