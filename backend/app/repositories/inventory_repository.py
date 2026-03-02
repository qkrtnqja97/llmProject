import asyncpg
from typing import List, Dict, Optional

class InventoryRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    # 📍 서비스(get_product_list)에서 호출하는 이름과 정확히 일치시켜야 합니다.
    async def get_products(self, skip: int, limit: int, search: str = "") -> Dict:
        search_query = f"%{search}%"
        
        # DDL에 따라 manufacturer_id와 part_number를 사용하여 조인하는 쿼리입니다.
        query = """
            WITH LatestPurchase AS (
                -- 제품별 가장 최근의 제조사 정보를 가져옴
                SELECT DISTINCT ON (po.part_number)
                    po.part_number,
                    m.name AS manufacturer_name
                FROM inventory_mgmt.purchase_orders po
                JOIN inventory_mgmt.manufacturers m ON po.manufacturer_id = m.manufacturer_id
                ORDER BY po.part_number, po.purchase_date DESC
            )
            SELECT 
                p.part_number,
                p.description,
                p.std_unit_cost,
                p.std_selling_price,
                COALESCE(lp.manufacturer_name, '정보 없음') AS manufacturer,
                COALESCE(c.current_quantity, 0) AS current_quantity,
                COUNT(*) OVER() as total_count
            FROM inventory_mgmt.products p
            LEFT JOIN inventory_mgmt.current_products c ON p.part_number = c.part_number
            LEFT JOIN LatestPurchase lp ON p.part_number = lp.part_number
            WHERE p.part_number ILIKE $1 OR p.description ILIKE $1
            ORDER BY p.part_number
            OFFSET $2 LIMIT $3
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, search_query, skip, limit)
            if not rows:
                return {"items": [], "total": 0}
            return {
                "items": [dict(r) for r in rows],
                "total": rows[0]["total_count"]
            }

    # 실시간 재고 현황 조회
    async def get_current_inventory(self, search: str = "") -> List[dict]:
        search_query = f"%{search}%"
        query = """
            SELECT * FROM inventory_mgmt.current_products
            WHERE part_number ILIKE $1 OR description ILIKE $1
            ORDER BY current_quantity ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, search_query)
            return [dict(r) for r in rows]

    # 제품 상세 조회 (모달 클릭 시 호출될 가능성이 높음)
    async def get_product_by_id(self, part_number: str) -> Optional[dict]:
        query = """
            SELECT 
                p.part_number,
                p.description,
                p.std_unit_cost,
                p.std_selling_price,
                -- 📍 조인을 통해 제조사 이름과 재고량을 가져옵니다.
                COALESCE(m.name, '정보 없음') AS manufacturer,
                COALESCE(c.current_quantity, 0) AS current_quantity
            FROM inventory_mgmt.products p
            LEFT JOIN inventory_mgmt.current_products c ON p.part_number = c.part_number
            LEFT JOIN (
                SELECT DISTINCT ON (part_number) part_number, manufacturer_id
                FROM inventory_mgmt.purchase_orders
                ORDER BY part_number, purchase_date DESC
            ) po ON p.part_number = po.part_number
            LEFT JOIN inventory_mgmt.manufacturers m ON po.manufacturer_id = m.manufacturer_id
            WHERE p.part_number = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, part_number)
            if row:
                # 📍 로그를 찍어서 확인해봅니다.
                result = dict(row)
                return result
            return None