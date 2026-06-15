from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from src.db.base import Base
import enum

class DriverStatus(str, enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class Driver(Base):
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)  # car, van, truck
    vehicle_plate = Column(String, unique=True, nullable=False)
    current_location_lat = Column(Float, nullable=True)
    current_location_lng = Column(Float, nullable=True)
    status = Column(Enum(DriverStatus), default=DriverStatus.AVAILABLE)
    rating = Column(Float, default=5.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="driver")