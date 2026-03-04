# app/api/v1/routes/inventory_router.py
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_inventory_controller, get_current_user
from app.schemas.inventory import ProductListResponse, InventoryResponse, ProductResponse
from typing import List

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/products", response_model=ProductListResponse)
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(30, le=100),
    search: str = Query("", description="검색어"),
    controller = Depends(get_inventory_controller)
):
    return await controller.list_products(skip, limit, search)

@router.get("/current", response_model=List[InventoryResponse])
async def get_current_inventory(
    search: str = Query("", description="검색어"),
    controller = Depends(get_inventory_controller),
    # current_user: dict = Depends(get_current_user) # 조회 권한 체크용
):
    return await controller.get_inventory(search)

@router.get("/products/{part_number}", response_model=ProductResponse)
async def get_product_detail(
    part_number: str,
    controller = Depends(get_inventory_controller)
):
    return await controller.get_detail(part_number)