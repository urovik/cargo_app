# main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.db.db import async_engine
from src.db.base import Base


from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.requests import Request

# Импортируем все роутеры
from src.auth.api import router as auth_router
from src.users.api import router as users_router
from src.drivers.api import router as drivers_router
from src.orders.api import router as orders_router
from src.admin.api import router as admin_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")
    yield
    print("Shutting down...")
    await async_engine.dispose()
    print("Database connections closed")

app = FastAPI(title="Cargo Delivery API", lifespan=lifespan)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# CORS (для продакшена настройте конкретные origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(drivers_router)
app.include_router(orders_router)
app.include_router(admin_router)

@app.get("/")
async def root():
    return {"message": "Cargo Delivery API"}



