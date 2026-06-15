import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from src.core.config import settings, load_rsa_keys

# Загружаем RSA ключи при старте
PRIVATE_KEY, PUBLIC_KEY = load_rsa_keys()


class JWTHandler:
    """Класс для работы с JWT токенами с использованием RSA (RS256)"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Создание access токена с использованием RSA приватного ключа
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.now(timezone.utc)
        })
        
        # Кодируем с RSA приватным ключом
        encoded_jwt = jwt.encode(
            to_encode, 
            PRIVATE_KEY,  # Используем приватный ключ
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Создание refresh токена с более долгим сроком жизни"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.now(timezone.utc)
        })
        
        encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Декодирование и верификация токена с использованием RSA публичного ключа
        """
        try:
            # Верифицируем с помощью публичного ключа
            payload = jwt.decode(
                token, 
                PUBLIC_KEY,  # Используем публичный ключ для верификации
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": True}
            )
            return payload
        except ExpiredSignatureError:
            print("Token has expired")
            return None
        except InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Проверка валидности токена с дополнительной проверкой типа"""
        payload = JWTHandler.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get("type") != token_type:
            print(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
        
        return payload
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        payload = JWTHandler.verify_token(token)
        return payload.get("sub") if payload else None