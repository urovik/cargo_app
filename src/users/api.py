# users/api.py

from fastapi import APIRouter, Depends, HTTPException
from src.auth.dependencies import get_current_user
from src.users.schemas import UserResponse, UserUpdate
from src.users.service import UserService  # создадим его

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(update_data: UserUpdate, current_user = Depends(get_current_user)):
    return await UserService.update_user(current_user.id, update_data)