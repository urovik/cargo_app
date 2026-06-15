from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.db.repository import SQLAlchemyRepository
from src.drivers.models import Driver, DriverStatus

class DriverRepository(SQLAlchemyRepository[Driver]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Driver)
    
    async def get_available_drivers(self) -> list[Driver]:
        query = select(self.model).where(
            self.model.status == DriverStatus.AVAILABLE,
            self.model.is_active == True
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_location(self, driver_id: int, lat: float, lng: float) -> Driver | None:
        query = (
            update(self.model)
            .where(self.model.id == driver_id)
            .values(current_location_lat=lat, current_location_lng=lng)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def update_status(self, driver_id: int, status: DriverStatus) -> Driver | None:
        query = (
            update(self.model)
            .where(self.model.id == driver_id)
            .values(status=status)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()