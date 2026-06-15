from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "cargo_delivery_db"
    DB_PORT: int = 5432
    DB_NAME: str = "cargo_delivery"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "pass"
    
    # JWT RSA
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

def load_rsa_keys():
    """Загрузка RSA ключей из файлов"""
    try:
        with open(settings.PRIVATE_KEY_PATH, "rb") as f:
            private_key = f.read()
        with open(settings.PUBLIC_KEY_PATH, "rb") as f:
            public_key = f.read()
        return private_key, public_key
    except FileNotFoundError as e:
        raise RuntimeError(
            f"RSA key file not found: {e}. "
            "Run: openssl genrsa -out src/certs/jwt-private.pem 2048 && "
            "openssl rsa -in src/certs/jwt-private.pem -pubout -out src/certs/jwt-public.pem"
        )