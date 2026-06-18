# orders/api.py
from fastapi import APIRouter, Depends, HTTPException
from src.auth.dependencies import get_current_user, require_role
from src.users.schemas import UserResponse
from src.orders.service import OrderService
from src.orders.schemas import OrderCreate, OrderUpdate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=dict)
async def create_order(
    order_data: OrderCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    return await OrderService.create_order(current_user.id, order_data)

@router.get("/", response_model=list[OrderResponse])
async def get_my_orders(current_user: UserResponse = Depends(get_current_user)):
    return await OrderService.get_user_orders(current_user.id)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    order = await OrderService.get_order_by_id(order_id, current_user.id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.get("/driver/orders")
async def get_driver_orders(
    current_user: UserResponse = Depends(require_role("driver"))
):
    """Получить все заказы, назначенные текущему водителю"""
    return await OrderService.get_driver_orders(current_user.id)

@router.patch("/{order_id}/driver-cancel")
async def driver_cancel_order(
    order_id: int,
    current_user: UserResponse = Depends(require_role("driver"))
):
    """Отмена заказа водителем (если заказ в статусе ACCEPTED)"""
    result = await OrderService.driver_cancel_order(order_id, current_user.id)
    if not result:
        raise HTTPException(400, "Cannot cancel order")
    return {"message": "Order cancelled by driver"}

# Аналогично добавьте остальные эндпоинты (update, cancel, accept, decline и т.д.)