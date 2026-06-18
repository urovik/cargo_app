# auth/api.py
from fastapi import APIRouter, Depends, HTTPException
from src.auth.service import AuthService
from src.auth.schemas import LoginRequest, RefreshTokenRequest, UserLoginResponse
from src.users.schemas import UserCreate, UserResponse
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    return await AuthService.register_user(user_data)

@router.post("/login", response_model=UserLoginResponse)
async def login(login_data: LoginRequest):
    return await AuthService.login_user(login_data)

@router.post("/refresh")
async def refresh(refresh_data: RefreshTokenRequest):
    return await AuthService.refresh_token(refresh_data.refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return current_user