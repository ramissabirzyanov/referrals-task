from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists
from redis import Redis

from app.models.referral_code import ReferralCode
from app.models.user import User
from app.schemas.referral_code import ReferralCodeCreate, ReferralCodeResponse, UserRefCodes


class ReferralCodeService:
    def __init__(self, db: AsyncSession, redis_client: Optional[Redis] = None):
        self.db = db
        self.redis_client = redis_client

    async def create_referral_code(
        self, referral_code: ReferralCodeCreate,
        current_user_id: int
    ) -> ReferralCode:
        new_referral_code = ReferralCode(**referral_code.model_dump(), owner_id=current_user_id)
        self.db.add(new_referral_code)
        await self.db.commit()
        await self.db.refresh(new_referral_code)
        await self.clear_user_referral_codes_cache(current_user_id)
        return new_referral_code

    async def get_user_referral_codes(self, owner_id: int) -> UserRefCodes:
        if self.redis_client:
            cache_key = f"user:{owner_id}:refcodes"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                cashed_refcodes = UserRefCodes.model_validate_json(cached_data)
                return cashed_refcodes

        result = await self.db.execute(
            select(ReferralCode).where(ReferralCode.owner_id == owner_id)
        )
        referral_codes = result.scalars().all()
        refcodes_pydantic = [
            ReferralCodeResponse.model_validate(refcode) for refcode in referral_codes
        ]

        if self.redis_client:
            await self.redis_client.setex(
                cache_key, 600, UserRefCodes(referral_codes=refcodes_pydantic).model_dump_json()
            )
        return UserRefCodes(referral_codes=refcodes_pydantic)

    async def clear_user_referral_codes_cache(self, owner_id: int) -> None:
        """Функция для очистки кеша."""
        if self.redis_client:
            cache_key = f"user:{owner_id}:refcodes"
            await self.redis_client.delete(cache_key)

    async def get_referral_code_by_code(self, code: str) -> ReferralCode:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.code == code))
        referral_code = result.scalars().first()
        return referral_code

    async def get_referral_code_by_id(self, code_id: int) -> ReferralCode:
        referral_code = await self.db.get(ReferralCode, code_id)
        return referral_code

    async def has_user_active_referral_code(self, owner_id: int) -> bool:
        result = await self.db.execute(
            select(exists().where(ReferralCode.owner_id == owner_id, ReferralCode.active is True))
        )
        return result.scalar()

    async def activate_referral_code(self, referral_code: ReferralCode) -> ReferralCode:
        referral_code.active = True
        await self.db.commit()
        await self.db.refresh(referral_code)
        await self.clear_user_referral_codes_cache(referral_code.owner_id)
        return referral_code

    async def delete_referral_code(self, referral_code: ReferralCode) -> dict:
        await self.db.delete(referral_code)
        await self.db.commit()
        await self.clear_user_referral_codes_cache(referral_code.owner_id)
        return {"detail": "Referral code deleted successfully"}

    async def get_referral_code_by_referrer_email(self, email: str) -> Optional[ReferralCode]:
        """
        Получает активный реферальный код по email реферера.
        """
        result = await self.db.execute(
            select(ReferralCode)
            .join(User, ReferralCode.owner_id == User.id)
            .where(User.email == email, ReferralCode.active is True)
        )
        referral_code = result.scalars().first()
        if referral_code is None:
            return None

        return referral_code

    async def get_invited_users_by_referrer_id(self, referrer_id: int) -> dict:
        user = await self.db.get(User, referrer_id)
        if user is None:
            raise ValueError("User not found")

        result = await self.db.execute(
            select(User)
            .where(User.invited_by_id == referrer_id)
        )
        invited_users = result.scalars().all()

        return {
            "user": user,
            "invited_users": invited_users
        }
