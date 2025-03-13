from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.referral_code import ReferralCode
from app.schemas.user import UserCreate, UserCreateByRefCode
from app.core.security import hash_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate) -> User:
        hashed_password = hash_password(user.password)
        new_user = User(email=user.email, hashed_password=hashed_password)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_email(self, email: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create_user_by_refcode(self, user: UserCreateByRefCode) -> Optional[User]:
        result = await self.db.execute(
            select(ReferralCode)
            .where(ReferralCode.code == user.referral_code, ReferralCode.active is True)
            .options(
                selectinload(ReferralCode.owner).selectinload(User.invited_users)
            )
        )
        referral_code = result.scalars().first()

        if not referral_code:
            return None

        new_user = await self.create_user(user)
        new_user.invited_by_id = referral_code.owner_id
        referral_code.owner.invited_users.append(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
