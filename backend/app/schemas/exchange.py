from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ExchangeListingCreate(BaseModel):
    coin_id: int

class ExchangeListingResponse(BaseModel):
    id: int
    coin_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExchangeOfferCreate(BaseModel):
    offered_coin_ids: Optional[List[int]] = None
    requested_coin_ids: Optional[List[int]] = None
    to_user_id: Optional[int] = None
    message: Optional[str] = None

class ExchangeOfferResponse(BaseModel):
    id: int
    offered_coin_ids: Optional[List[int]] = None
    requested_coin_ids: List[int]
    from_user_id: int
    to_user_id: int
    status: str  # теперь строка, не Enum
    message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True