import jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_jwt
from app.schemas.auth import TokenData
from app.services.user_service import UserService
from app.db.session import get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user