# users/service.py
from src.db.db_manager import TransactionDbManager
from src.users.schemas import UserUpdate, UserResponse

class UserService:
    @staticmethod
    async def update_user(user_id: int, update_data: UserUpdate) -> UserResponse:
        async with TransactionDbManager() as db:
            user = await db.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            updated = await db.user_repo.update(
                user_id, 
                **update_data.model_dump(exclude_unset=True)   # <-- исправлено
            )
            await db.commit()
            return UserResponse.model_validate(updated)