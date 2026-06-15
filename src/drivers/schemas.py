from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum

class DriverStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class DriverBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    vehicle_type: str = Field(..., pattern=r'^(car|van|truck)$')
    vehicle_plate: str = Field(..., min_length=5, max_length=10)

class DriverCreate(DriverBase):
    password: str = Field(..., min_length=6, max_length=100)

class DriverUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    current_location_lat: Optional[float] = Field(None, ge=-90, le=90)
    current_location_lng: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[DriverStatus] = None
    is_active: Optional[bool] = None

class DriverResponse(DriverBase):
    id: int
    status: DriverStatus
    rating: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DriverLocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)