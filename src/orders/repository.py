from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime
from src.db.repository import SQLAlchemyRepository
from src.orders.models import Order, OrderStatus

class OrderRepository(SQLAlchemyRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)
    
    async def get_by_user_id(self, user_id: int) -> list[Order]:
        query = select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_driver_id(self, driver_id: int) -> list[Order]:
        query = select(self.model).where(self.model.driver_id == driver_id).order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_pending_orders(self) -> list[Order]:
        query = select(self.model).where(self.model.status == OrderStatus.PENDING).order_by(self.model.created_at.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def accept_order(self, order_id: int, driver_id: int) -> Order | None:
        query = (
            update(self.model)
            .where(
                and_(
                    self.model.id == order_id,
                    self.model.status == OrderStatus.PENDING
                )
            )
            .values(
                driver_id=driver_id,
                status=OrderStatus.ACCEPTED,
                accepted_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def cancel_order(self, order_id: int, user_id: int = None) -> Order | None:
        conditions = [self.model.id == order_id, self.model.status == OrderStatus.PENDING]
        if user_id:
            conditions.append(self.model.user_id == user_id)
        
        query = (
            update(self.model)
            .where(and_(*conditions))
            .values(
                status=OrderStatus.CANCELLED,
                cancelled_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def update_order_status(self, order_id: int, status: OrderStatus, driver_id: int = None) -> Order | None:
        values = {"status": status, "updated_at": datetime.utcnow()}
        
        if status == OrderStatus.DELIVERED:
            values["delivered_at"] = datetime.utcnow()
        
        conditions = [self.model.id == order_id]
        if driver_id:
            conditions.append(self.model.driver_id == driver_id)
        
        query = (
            update(self.model)
            .where(and_(*conditions))
            .values(**values)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()