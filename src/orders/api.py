from fastapi import APIRouter, HTTPException, Depends
from src.orders.service import OrderService
from src.orders.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

# Временная заглушка для get_current_user
async def get_current_user():
    """Временная заглушка для авторизации"""
    return {"id": 1, "username": "test_user"}

@router.post("/", response_model=dict)
async def create_order(order_data: OrderCreate):
    """Создание нового заказа"""
    try:
        current_user = await get_current_user()
        result = await OrderService.create_order(current_user["id"], order_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list)
async def get_user_orders():
    """Получение всех заказов пользователя"""
    current_user = await get_current_user()
    orders = await OrderService.get_user_orders(current_user["id"])
    return orders

@router.get("/{order_id}")
async def get_order(order_id: int):
    """Получение конкретного заказа"""
    current_user = await get_current_user()
    order = await OrderService.get_order_by_id(order_id, current_user["id"])
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order