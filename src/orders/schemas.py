from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    pickup_address: str = Field(..., min_length=5, max_length=500)
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lng: float = Field(..., ge=-180, le=180)
    delivery_address: str = Field(..., min_length=5, max_length=500)
    delivery_lat: float = Field(..., ge=-90, le=90)
    delivery_lng: float = Field(..., ge=-180, le=180)
    cargo_description: str = Field(..., min_length=3, max_length=1000)
    cargo_weight: float = Field(..., gt=0, le=10000)
    cargo_volume: Optional[float] = Field(None, gt=0, le=100)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    pickup_address: Optional[str] = Field(None, min_length=5, max_length=500)
    delivery_address: Optional[str] = Field(None, min_length=5, max_length=500)
    cargo_description: Optional[str] = Field(None, min_length=3, max_length=1000)
    status: Optional[OrderStatus] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    driver_id: Optional[int]
    price: float
    distance_km: Optional[float]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    accepted_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True