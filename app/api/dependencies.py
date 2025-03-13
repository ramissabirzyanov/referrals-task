import jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_jwt
from app.schemas.auth import TokenData
from app.services.user_service import UserService
from app.services.referral_code_service import ReferralCodeService
from app.db.session import get_db
from app.models.user import User
from app.models.referral_code import ReferralCode
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_jwt(token)
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        token_data = TokenData(email=email)
        user_service = UserService(db)
        user = await user_service.get_user_by_email(email=token_data.email)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def check_existing_and_owner_referral_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReferralCode:

    """Проверяет существование реферального кода и его принадлежность пользователю"""

    service = ReferralCodeService(db)
    referral_code = await service.get_referral_code_by_id(code_id)

    if not referral_code:
        raise HTTPException(
            status_code=404,
            detail="Referral code not found"
        )

    if referral_code.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not own this referral code"
        )

    return referral_code
