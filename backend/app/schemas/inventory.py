# app/schemas/inventory.py
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List
from decimal import Decimal

# --- 제품 관리 (Products) ---
class ProductBase(BaseModel):
    part_number: str
    description: Optional[str] = None
    std_unit_cost: Decimal = 0
    std_selling_price: Decimal = 0
    manufacturer: Optional[str] = "정보 없음"
    current_quantity: Optional[int] = 0

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]

# --- 재고 현황 (Current Inventory) ---
class InventoryResponse(BaseModel):
    part_number: str
    description: Optional[str] = None
    current_quantity: int
    last_updated: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)