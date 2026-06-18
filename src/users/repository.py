from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.db.repository import SQLAlchemyRepository
from src.users.models import User

class UserRepository(SQLAlchemyRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> User | None:
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> User | None:
        query = select(self.model).where(self.model.phone == phone)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User | None:
        query = select(self.model).where(self.model.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    # users/repository.py (добавить)
    async def update_last_login(self, user_id: int) -> None:
        
        query = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.session.execute(query)
        await self.session.flush()
