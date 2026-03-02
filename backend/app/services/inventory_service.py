# app/services/inventory_service.py
from fastapi import HTTPException, status
from app.repositories.inventory_repository import InventoryRepository

class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self.repo = repo

    async def get_product_list(self, skip: int, limit: int, search: str):
        return await self.repo.get_products(skip, limit, search)

    async def get_inventory_status(self, search: str):
        return await self.repo.get_current_inventory(search)

    async def get_product_detail(self, part_number: str):
        product = await self.repo.get_product_by_id(part_number)
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        return product