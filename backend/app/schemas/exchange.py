from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models import OfferStatus

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
    offered_coin_id: int
    requested_coin_id: int
    message: Optional[str] = None

class ExchangeOfferResponse(BaseModel):
    id: int
    offered_coin_id: int
    requested_coin_id: int
    from_user_id: int
    to_user_id: int
    status: OfferStatus
    message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True