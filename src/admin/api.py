from fastapi import APIRouter, Depends, HTTPException
from src.auth.dependencies import require_role
from src.users.schemas import UserResponse
from src.admin.service import AdminService
from src.orders.schemas import OrderResponse, OrderUpdate
from src.users.schemas import UserUpdate as UserUpdateSchema
from src.drivers.schemas import DriverUpdate

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role("admin"))])

# Управление заказами
@router.get("/orders", response_model=list[OrderResponse])
async def get_all_orders():
    return await AdminService.get_all_orders()

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    await AdminService.delete_order(order_id)
    return {"message": "Order deleted"}

@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def admin_update_order(order_id: int, update_data: OrderUpdate):
    return await AdminService.admin_update_order(order_id, update_data)

# Блокировка пользователей
@router.patch("/users/{user_id}/block")
async def block_user(user_id: int):
    await AdminService.block_user(user_id, is_active=False)
    return {"message": "User blocked"}

@router.patch("/users/{user_id}/unblock")
async def unblock_user(user_id: int):
    await AdminService.block_user(user_id, is_active=True)
    return {"message": "User unblocked"}

# Блокировка водителей
@router.patch("/drivers/{driver_id}/block")
async def block_driver(driver_id: int):
    await AdminService.block_driver(driver_id, is_active=False)
    return {"message": "Driver blocked"}

@router.patch("/drivers/{driver_id}/unblock")
async def unblock_driver(driver_id: int):
    await AdminService.block_driver(driver_id, is_active=True)
    return {"message": "Driver unblocked"}