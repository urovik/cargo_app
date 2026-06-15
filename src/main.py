# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from src.db.db import async_engine
from src.db.base import Base
from src.orders.api import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await async_engine.dispose()
    print("Database connections closed")

app = FastAPI(
    title="API cargo_delivery",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(orders_router)

@app.get("/")
async def root():
    return {"message": "Cargo Delivery API"}

