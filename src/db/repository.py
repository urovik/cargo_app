# db/repository.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func

ModelType = TypeVar('ModelType')

class AbstractRepository(ABC, Generic[ModelType]):
    """Абстрактный репозиторий с базовыми CRUD операциями"""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
    
    @abstractmethod
    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить все записи с пагинацией"""
        pass
    
    @abstractmethod
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись по ID"""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить запись по ID"""
        pass


class SQLAlchemyRepository(AbstractRepository[ModelType]):
    """Реализация репозитория для SQLAlchemy"""
    
    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def delete(self, id: int) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0
    
    async def count(self) -> int:
        """Дополнительный метод: подсчет записей"""
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar()
    
    async def exists(self, id: int) -> bool:
        """Дополнительный метод: проверка существования"""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None