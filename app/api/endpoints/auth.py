from typing import Annotated
from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from redis import Redis

from app.services.email import get_email_service, EmailService
from app.db.database import get_db_session
from app.db.models import User
from app.api.schemas.user import UserRegister
from app.core.config import settings
from app.core.redis import get_redis
from app.core.security import create_token, get_email_from_token, hash_password

auth_router = APIRouter(prefix="/auth", tags=['auth'])

@auth_router.post("/register")
async def register(register_user_data: UserRegister,
                   response: Response, 
                   session: Annotated[AsyncSession, Depends(get_db_session)],
                   email_service: Annotated[EmailService, Depends(get_email_service)],
                   cache: Annotated[Redis, Depends(get_redis)]
                ):
    register_dict = register_user_data.model_dump()

    new_user = User(email=register_dict.get("email"),
                    password=hash_password(register_dict.get("password")),
                    role=register_dict.get("role"))

    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    except IntegrityError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"User with provided email({register_dict["email"]}) already exists"}

    verification_token = create_token({"sub": register_dict["email"]}, settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)

    cache.set(f"verification_token:{register_dict.get("email")}", 
              verification_token, 
              ex=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES*60)
    
    await email_service.send_message("Email confirmation", f"""To verify your email follow the link: \n
                                     {settings.DOMAIN}/auth/verify/{verification_token}""", 
                                     register_dict.get("email"))

@auth_router.get("/verify/{verification_token}")
async def verify_email(verification_token: str, 
                       session: Annotated[AsyncSession, Depends(get_db_session)], 
                       cache: Annotated[Redis, Depends(get_redis)]):
    user_email = get_email_from_token(verification_token)

    token_value = cache.get(f"verification_token:{user_email}")

    if not token_value:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")

    result = await session.execute(select(User).where(User.email == user_email))
    user: User = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.is_verified:
        return {"message":"Email is already verified"}
    
    await session.execute(update(User).where(User.email == user_email).values(is_verified = True))
    await session.commit()
    cache.delete(f"verification_token:{user_email}")

    return {"message":"Email is verified"}