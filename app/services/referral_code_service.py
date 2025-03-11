from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from redis import Redis

from app.models.referral_code import ReferralCode
from app.schemas.referral_code import ReferralCodeCreate, ReferralCodeResponse, ReferralCodeBase, UserRefCodes


class ReferralCodeService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis_client = redis


    async def create_referral_code(
            self, referral_code: ReferralCodeCreate,
            current_user_id: int
    ) -> ReferralCodeResponse:

        new_referral_code = ReferralCode(**referral_code.model_dump(), owner_id=current_user_id)
        self.db.add(new_referral_code)
        await self.db.commit()
        await self.db.refresh(new_referral_code)
        return ReferralCodeResponse.model_validate(new_referral_code)


    async def activate_referral_code(self, code_id: int) -> ReferralCodeResponse:
        referral_code = await self.db.get(ReferralCode, code_id)
        if not referral_code:
            raise ValueError("The referral code is not founded")

        existing_active_code = await self.db.execute(
            select(ReferralCode)
            .where(
                ReferralCode.owner_id == referral_code.owner_id,
                ReferralCode.active == True
            )
        )
        if existing_active_code.scalars().first():
            raise ValueError("The user has active referral code already")
        referral_code.active = True
        await self.db.commit()
        await self.db.refresh(referral_code)
        return referral_code


    async def get_user_referral_codes(self, owner_id: int) -> UserRefCodes:
        cache_key = f"user:{owner_id}:refcodes"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
                cashed_refcodes = UserRefCodes.model_validate_json(cached_data)
                return cashed_refcodes

        result = await self.db.execute(select(ReferralCode).where(ReferralCode.owner_id == owner_id))
        referral_codes = result.scalars().all()
        refcodes_pydantic = [ReferralCodeBase.model_validate(refcode) for refcode in referral_codes]
        await self.redis_client.setex(cache_key, 600, UserRefCodes(refcodes=refcodes_pydantic).model_dump_json())
        return UserRefCodes(referral_codes=refcodes_pydantic)


    async def get_referral_code_by_code(self, code: str) -> ReferralCode:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.code == code))
        referral_code = result.scalars().first()
        return referral_code


    async def get_referral_code_detail(self, code_id: int, owner_id: int) -> ReferralCodeResponse:
        result = await self.db.execute(
        select(ReferralCode).where(ReferralCode.id == code_id, ReferralCode.owner_id == owner_id)
        )
        referral_code = result.scalars().first()
        return ReferralCodeResponse.model_validate(referral_code)


    async def delete_referral_code(self, code_id: int, owner_id: int) -> bool:
        result = await self.db.execute(
            select(ReferralCode).where(ReferralCode.id == code_id, ReferralCode.owner_id == owner_id)
        )
        referral_code = result.scalars().first()
        
        if not referral_code:
            return False
        
        await self.db.execute(delete(ReferralCode).where(ReferralCode.id == code_id))
        await self.db.commit()
        return True 

