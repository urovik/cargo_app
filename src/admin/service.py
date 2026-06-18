from fastapi import HTTPException

from src.db.db_manager import TransactionDbManager
from src.orders.schemas import OrderResponse, OrderUpdate
from src.users.schemas import UserResponse
from src.drivers.schemas import DriverResponse

class AdminService:
    @staticmethod
    async def get_all_orders():
        async with TransactionDbManager() as db:
            orders = await db.order_repo.get_all()
            return [OrderResponse.model_validate(o) for o in orders]

    @staticmethod
    async def delete_order(order_id: int):
        async with TransactionDbManager() as db:
            deleted = await db.order_repo.delete(order_id)
            if not deleted:
                raise HTTPException(404, "Order not found")
            await db.commit()

    @staticmethod
    async def admin_update_order(order_id: int, update_data: OrderUpdate):
        async with TransactionDbManager() as db:
            order = await db.order_repo.update(order_id, **update_data.model_dump(exclude_unset=True))
            if not order:
                raise HTTPException(404, "Order not found")
            await db.commit()
            return OrderResponse.model_validate(order)

    @staticmethod
    async def block_user(user_id: int, is_active: bool):
        async with TransactionDbManager() as db:
            user = await db.user_repo.update(user_id, is_active=is_active)
            if not user:
                raise HTTPException(404, "User not found")
            await db.commit()

    @staticmethod
    async def block_driver(driver_id: int, is_active: bool):
        async with TransactionDbManager() as db:
            driver = await db.driver_repo.update(driver_id, is_active=is_active)
            if not driver:
                raise HTTPException(404, "Driver not found")
            await db.commit()