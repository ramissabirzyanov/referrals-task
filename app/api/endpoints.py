from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

from app.core.redis import get_redis
from app.core.security import encode_jwt, validate_password
from app.schemas.auth import Token
from app.models.user import User
from app.models.referral_code import ReferralCode
from app.api.dependencies import get_current_user, check_existing_and_owner_referral_code
from app.schemas.user import UserResponse, UserCreate, UserCreateByRefCode
from app.schemas.referral_code import UserRefCodes, ReferralCodeResponse, ReferralCodeCreate, ReferralsResponse
from app.services.user_service import UserService
from app.services.referral_code_service import ReferralCodeService
from app.db.session import get_db


router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    db_user = await service.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return await service.create_user(user)


@router.post("/register/referral_code", response_model=UserResponse)
async def сreate_user_by_refcode(
    user_data: UserCreateByRefCode,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    new_user = await service.create_user_by_refcode(user_data)

    if new_user is None:
        raise HTTPException(status_code=400, detail="Invalid or inactive referral code.")

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
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


@router.post("/create_refcode", response_model=ReferralCodeResponse)
async def create_referral_code(
    code_data: ReferralCodeCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)

):
    service = ReferralCodeService(db, redis_client)
    refcode = await service.get_referral_code_by_code(code_data.code)
    if refcode:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Same code exists already")
    return await service.create_referral_code(code_data, current_user_id=current_user.id)
    

@router.get("/refcodes", response_model=UserRefCodes)
async def get_user_referrals(
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    service = ReferralCodeService(db, redis_client)
    return await service.get_user_referral_codes(current_user.id)


@router.get("/{referrer_id}/referrals", response_model=ReferralsResponse)
async def get_invited_users_by_referrer_id(
    referrer_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ReferralCodeService(db)
    try:
        return await service.get_invited_users_by_referrer_id(referrer_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/refcodes/{code_id}", response_model=ReferralCodeResponse)
async def get_referral_code_detail(
    db: AsyncSession = Depends(get_db),
    referral_code: ReferralCode = Depends(check_existing_and_owner_referral_code),
):
    service = ReferralCodeService(db)
    refcode_detail =  await service.get_referral_code_detail(referral_code)
    return refcode_detail


@router.delete("/refcodes/{code_id}")
async def delete_referral_code(
    db: AsyncSession = Depends(get_db),
    referral_code: ReferralCode = Depends(check_existing_and_owner_referral_code),
    redis_client: Redis = Depends(get_redis)
):
    service = ReferralCodeService(db, redis_client)
    return await service.delete_referral_code(referral_code)


@router.patch("/refcodes/{code_id}", response_model=ReferralCodeResponse)
async def activate_referral_code(
    db: AsyncSession = Depends(get_db),
    referral_code: ReferralCode = Depends(check_existing_and_owner_referral_code),
    redis_client: Redis = Depends(get_redis)
):
    service = ReferralCodeService(db, redis_client)
    if await service.has_user_active_referral_code(referral_code.owner_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has an active referral code already")

    active_referral_code = await service.activate_referral_code(referral_code)
    return active_referral_code


@router.get("/refcodes/{email}", response_model=ReferralCodeResponse)
async def get_referral_code_by_email(
    email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReferralCodeService(db)
    referral_code = await service.get_referral_code_by_referrer_email(email)

    if referral_code is None:
        raise HTTPException(status_code=404, detail="Active referral code not found")

    return referral_code
