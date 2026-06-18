from src.db.db_manager import TransactionDbManager
from src.auth.security import verify_password, get_password_hash
from src.auth.jwt import JWTHandler
from src.auth.schemas import LoginRequest, Token, UserLoginResponse
from src.users.schemas import UserCreate, UserResponse
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class AuthService:
    
    @staticmethod
    async def register_user(user_data: UserCreate) -> UserResponse:
        """Регистрация нового пользователя"""
        async with TransactionDbManager() as db:
            # Проверка email
            existing_email = await db.user_repo.get_by_email(user_data.email)
            if existing_email:
                raise HTTPException(400, detail="Email already registered")
            # Проверка username
            existing_username = await db.user_repo.get_by_username(user_data.username)
            if existing_username:
                raise HTTPException(400, detail="Username already taken")
            # Проверка телефона
            existing_phone = await db.user_repo.get_by_phone(user_data.phone)
            if existing_phone:
                raise HTTPException(400, detail="Phone already registered")
            
            # Хэшируем пароль с помощью bcrypt через passlib
            hashed_password = get_password_hash(user_data.password)
            
            # Создаем пользователя
            user = await db.user_repo.create(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                phone=user_data.phone,
                role=user_data.role,
                password_hash=hashed_password
            )
            
            await db.commit()
            logger.info(f"New user registered: {user.username} (ID: {user.id})")
            
            return UserResponse.model_validate(user)
    
    @staticmethod
    async def login_user(login_data: LoginRequest) -> UserLoginResponse:
        """Аутентификация пользователя и выдача JWT токенов"""
        async with TransactionDbManager() as db:
            # Ищем пользователя по username или phone
            user = await db.user_repo.get_by_username(login_data.username)
            if not user:
                user = await db.user_repo.get_by_email(login_data.username)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Проверяем пароль
            if not verify_password(login_data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Проверяем активен ли пользователь
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is disabled"
                )
            
            # Обновляем время последнего входа
            await db.user_repo.update_last_login(user.id)
            await db.commit()
            
            # Создаем JWT токены с помощью PyJWT
            token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
            access_token = JWTHandler.create_access_token(token_data)
            refresh_token = JWTHandler.create_refresh_token(token_data)
            
            logger.info(f"User logged in: {user.username} (ID: {user.id})")
            
            return UserLoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user_id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.value
            )
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Token:
        """Обновление access токена с использованием refresh токена"""
        # Верифицируем refresh токен
        payload = JWTHandler.verify_token(refresh_token, token_type="refresh")
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )
        
        # Создаем новый access токен
        new_token_data = {"sub": str(user_id), "username": payload.get("username"), "role": payload.get("role")}
        new_access_token = JWTHandler.create_access_token(new_token_data)
        
        logger.info(f"Token refreshed for user ID: {user_id}")
        
        return Token(
            access_token=new_access_token,
            refresh_token=refresh_token
        )