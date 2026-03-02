# app/api/v1/controllers/inventory_controller.py
from app.services.inventory_service import InventoryService

class InventoryController:
    def __init__(self, service: InventoryService):
        self.service = service

    async def list_products(self, skip: int, limit: int, search: str):
        return await self.service.get_product_list(skip, limit, search)

    async def get_inventory(self, search: str):
        return await self.service.get_inventory_status(search)

    async def get_detail(self, part_number: str):
        return await self.service.get_product_detail(part_number)