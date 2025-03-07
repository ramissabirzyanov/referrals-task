from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate) -> UserResponse:
        hashed_password = hash_password(user.password)
        new_user = User(email=user.email, hashed_password=hashed_password)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return UserResponse.model_validate(new_user)

    async def get_user_by_email(self, email: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()