from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.referral_code import ReferralCode
from app.schemas.referral_code import ReferralCodeCreate, ReferralCodeResponse


class ReferralCodeService:
    def __init__(self, db: AsyncSession):
        self.db = db

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
            raise ValueError("Реферальный код не найден")

        existing_active_code = await self.db.execute(
            select(ReferralCode)
            .where(
                ReferralCode.owner_id == referral_code.owner_id,
                ReferralCode.active == True
            )
        )
        if existing_active_code.scalars().first():
            raise ValueError("У пользователя уже есть активный реферальный код")

        referral_code.active = True
        await self.db.commit()
        await self.db.refresh(referral_code)
        return referral_code

    async def get_user_referral_codes(self, owner_id: int) -> list[ReferralCodeResponse]:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.owner_id == owner_id))
        referral_codes = result.scalars().all()
        return referral_codes
