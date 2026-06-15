from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async_engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:Vy7kk5lbnem@localhost/cargo-delivery-db")


async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)



