from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import encode_jwt, validate_password
from app.schemas.auth import Token
from app.models.user import User
from app.models.referral_code import ReferralCode
from app.api.dependencies import get_current_user
from app.schemas.user import UserResponse, UserCreate, Users
from app.schemas.referral_code import UserRefCodes
from app.services.user_service import UserService
from app.services.referral_code_service import ReferralCodeService
from app.db.session import get_db


router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    db_user = await user_service.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(form_data.username)
    if not user or not validate_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = encode_jwt({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/{user_id}/refcodes", response_model=UserRefCodes)
async def get_user_referrals(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ReferralCodeService(db)
    user_referral_code = await service.get_user_referral_codes(current_user.id)
    return UserRefCodes(refcodes=user_referral_code)
