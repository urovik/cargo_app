from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from src.db.base import Base
import enum

class OrderStatus(str, enum.Enum):
    PENDING = "pending"  # ожидает водителя
    ACCEPTED = "accepted"  # водитель принял
    PICKED_UP = "picked_up"  # груз забран
    IN_TRANSIT = "in_transit"  # в пути
    DELIVERED = "delivered"  # доставлен
    CANCELLED = "cancelled"  # отменен

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id', ondelete='SET NULL'), nullable=True)
    
    # Адреса
    pickup_address = Column(String, nullable=False)
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_lat = Column(Float, nullable=False)
    delivery_lng = Column(Float, nullable=False)
    
    # Информация о грузе
    cargo_description = Column(Text, nullable=False)
    cargo_weight = Column(Float, nullable=False)  # в кг
    cargo_volume = Column(Float, nullable=True)  # в м³
    
    # Детали заказа
    price = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    driver = relationship("Driver", back_populates="orders")