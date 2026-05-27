from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models import MetalType, CoinCondition

class CoinImageBase(BaseModel):
    image_path: str
    is_obverse: bool = True

class CoinImageResponse(CoinImageBase):
    id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class CoinBase(BaseModel):
    name: str
    year: int
    country: str
    denomination: str
    metal: MetalType
    condition: CoinCondition
    purchase_price: Optional[float] = None
    estimated_value: float

class CoinCreate(CoinBase):
    pass

class CoinUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    denomination: Optional[str] = None
    metal: Optional[MetalType] = None
    condition: Optional[CoinCondition] = None
    purchase_price: Optional[float] = None
    estimated_value: Optional[float] = None

class CoinResponse(CoinBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    images: List[CoinImageResponse] = []
    
    class Config:
        from_attributes = True

class CoinFilterParams(BaseModel):
    country: Optional[str] = None
    metal: Optional[MetalType] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    condition: Optional[CoinCondition] = None
    search: Optional[str] = None