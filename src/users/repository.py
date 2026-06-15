from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.repository import SQLAlchemyRepository
from src.users.models import User

class UserRepository(SQLAlchemyRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> User | None:
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User | None:
        query = select(self.model).where(self.model.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()