from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
from app.schemas.user import UserResponse


class ReferralCodeBase(BaseModel):
    code: str
    expires_at: datetime
    active: bool = False

    class Config:
        from_attributes = True


class ReferralCodeCreate(ReferralCodeBase):
    pass


class ReferralCodeResponse(ReferralCodeBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
    
    @field_validator('expires_at')
    def check_expires_at(cls, expires_at: datetime) -> datetime:
        if expires_at and expires_at < datetime.now(timezone.utc):
            raise ValueError("Code expiration date is over")
        return expires_at


class ReferralsResponse(BaseModel):
    user: UserResponse
    invited_users: list[UserResponse] = []

    class Config:
        from_attributes = True


class UserRefCodes(BaseModel):
    referral_codes: list[ReferralCodeResponse]
    
    class Config:
        from_attributes = True
