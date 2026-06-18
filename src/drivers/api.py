# drivers/api.py
from fastapi import APIRouter, Depends, HTTPException
from src.auth.dependencies import get_current_user, require_role
from src.drivers.schemas import DriverResponse, DriverUpdate, DriverLocationUpdate
from src.drivers.service import DriverService
from src.users.schemas import UserResponse

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.get("/available", response_model=list[DriverResponse])
async def get_available_drivers():
    return await DriverService.get_available_drivers()

@router.put("/me/location")
async def update_location(
    location: DriverLocationUpdate,
    current_user: UserResponse = Depends(require_role("driver"))
):
    return await DriverService.update_location(current_user.id, location)

