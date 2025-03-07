from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.referral_code import ReferralCode
from app.schemas.referral_code import ReferralCodeCreate, ReferralCodeResponse

class ReferralCodeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_referral_code(self, referral_code: ReferralCodeCreate) -> ReferralCodeResponse:
        db_referral_code = ReferralCode(**referral_code.dict())
        self.db.add(db_referral_code)
        await self.db.commit()
        await self.db.refresh(db_referral_code)
        return ReferralCodeResponse.from_orm(db_referral_code)

    async def get_referral_code_by_owner_id(self, owner_id: int) -> ReferralCode:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.owner_id == owner_id))
        return result.scalars().first()