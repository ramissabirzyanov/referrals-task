from typing import List

from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserResponse


class ReferralCodeBase(BaseModel):
    code: str
    expires_at: datetime


class ReferralCodeCreate(ReferralCodeBase):
    pass


class ReferralCodeResponse(ReferralCodeBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class ReferralsResponse(BaseModel):
    user: UserResponse
    invited_users: List[UserResponse] = []

    class Config:
        from_attributes = True