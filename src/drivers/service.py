# drivers/servic
from src.db.db_manager import TransactionDbManager
from src.drivers.schemas import DriverResponse, DriverLocationUpdate

class DriverService:
    @staticmethod
    async def get_available_drivers():
        async with TransactionDbManager() as db:
            drivers = await db.driver_repo.get_available_drivers()
            return [DriverResponse.model_validate(d) for d in drivers]

    @staticmethod
    async def update_location(driver_id: int, location: DriverLocationUpdate):
        async with TransactionDbManager() as db:
            driver = await db.driver_repo.update_location(
                driver_id, location.lat, location.lng
            )
            await db.commit()
            if not driver:
                raise ValueError("Driver not found")
            return DriverResponse.model_validate(driver)