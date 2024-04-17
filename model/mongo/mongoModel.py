from pydantic import BaseModel, Field
from typing import List

# no request; yes response 

class MongoOutput(BaseModel):
    product_id: str = Field(..., description="User's name")
    vendor: str = Field(..., ge=18, le=100, description="User's age (should be between 18 and 100)")
    variants_id: str = Field(..., unique=True, description="User's city (should be unique)")
    title: str = Field(..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="User's email (should be valid)")
    variants_title: str = Field(..., min_length=8, max_length=50, description="User's password (should be between 8 and 50 characters)")
    price: float = Field(..., description="User's name")
    product_type: str = Field(..., description="User's name")
    weight: float = Field(..., description="User's name")
    weight_unit: str = Field(..., description="User's name")
    sku: str = Field(..., description="User's name")
    grams: float = Field(..., description="User's name")
    inventory_item_id: str = Field(..., description="User's name")
    inventory_quantity: float = Field(..., description="User's name")
    collections: List[str] = Field(..., description="User's name")
    available: int = Field(..., description="User's name")
    unavailabe: int = Field(..., description="User's name")
    on_hand: int = Field(..., description="User's name")
    committed: int = Field(..., description="User's name")
    sales_channel: List[int] = Field(..., description="User's name")



# 检查模型是否有效
MongoOutput(name="John", age=30, city="New York", email="john@example.com", password="12345678")