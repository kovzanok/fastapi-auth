from fastapi import HTTPException, status
import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from app.core.config import settings

def create_token(data: dict, expire_minutes: int):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

def get_email_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")

        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return email

password_hash = PasswordHash.recommended()

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def hash_password(password: str) -> str:
    return password_hash.hash(password)