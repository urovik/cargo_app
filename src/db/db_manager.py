# db/transaction_manager.py (обновленный)
from .db import async_session
from src.users.repository import UserRepository
from src.orders.repository import OrderRepository
from src.drivers.repository import DriverRepository

class TransactionDbManager:
    def __init__(self):
        self.session = async_session()
    
    async def __aenter__(self):
        self.user_repo = UserRepository(self.session)
        self.order_repo = OrderRepository(self.session)
        self.driver_repo = DriverRepository(self.session)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        
        await self.session.close()
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()