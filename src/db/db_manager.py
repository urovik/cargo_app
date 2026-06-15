from .db import async_session


class TransactionDbManager:

    def __init__(self):
        self.session = async_session()

    async def __aenter__(self):
        # наши репозитории здесь создаются
        pass

    async def __aexit__(self, exc_type, *args):
        if exc_type:
            await self.rollback()
        await self.session.rollback()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
