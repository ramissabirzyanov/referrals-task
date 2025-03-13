from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True


class UserCreateByRefCode(UserCreate):
    referral_code: str


class UserResponse(UserBase):
    id: int
    invited_by_id: int | None = None

    class Config:
        from_attributes = True
