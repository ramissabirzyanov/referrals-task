import datetime

from app.core.settings import settings

import jwt
import bcrypt


ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
PRIVATE_KEY = settings.PRIVATE_KEY_PATH.read_text()
PUBLIC_KEY = settings.PUBLIC_KEY_PATH.read_text()


def encode_jwt(
    payload: dict,
    private_key: str = PRIVATE_KEY,
    algorithm: str = ALGORITHM,
    expires_minutes: datetime.timedelta = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
):
    """
    Кодирует данные в JWT токен.
    """
    to_encode = payload.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now + expires_minutes
    to_encode.update(exp=expires_at, iat=now)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str,
    public_key: str = PUBLIC_KEY,
    algorithm=ALGORITHM
):
    """
    Декодирует JWT токен и возвращает данные.
    """
    try:
        decoded = jwt.decode(token, public_key, algorithms=[algorithm])
        return decoded
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid token") from e


def hash_password(password: str) -> bytes:
    """
    Хеширует пароль с использованием bcrypt.
    """
    salt = bcrypt.gensalt()
    pass_bytes = password.encode()
    hashed_password = bcrypt.hashpw(pass_bytes, salt)
    return hashed_password.decode('utf-8')


def validate_password(password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль хешированному паролю.
    """
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_password_bytes)
