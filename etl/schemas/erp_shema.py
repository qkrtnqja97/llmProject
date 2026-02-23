# etl/schemas/erp_shema.py

from pydantic import BaseModel

class ERPRecord(BaseModel):
    id: int
    product_name: str
    description: str
    quantity: int
    price: float