from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from redis.asyncio import Redis

from app.services.email import EmailService
from app.db.models import User
from app.core.config import settings
from app.core.security import create_token, get_email_from_token, hash_password, verify_password
from app.exceptions.auth import InvalidCredentials, UserAlreadyExists, InvalidToken, UserNotFound, AlreadyVerifiedUser, UserNotVerified

class AuthService():
    def __init__(self, cache: Redis, session: AsyncSession, email_service: EmailService):
        self.session = session
        self.cache = cache
        self.email_service = email_service

    async def register(self, email: str, password: str, role: str):
        new_user = User(email=email,
                    password=hash_password(password),
                    role=role)

        try:
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExists()
            
        await self._send_verification_email(email)
    
    async def verify(self, verification_token: str):
        user_email = get_email_from_token(verification_token)

        token_value = await self.cache.get(f"verification_token:{user_email}")

        if not token_value:
            raise InvalidToken()

        result = await self.session.execute(select(User).where(User.email == user_email))
        user: User = result.scalars().first()

        if not user:
            raise UserNotFound()
 
        if user.is_verified:
            raise AlreadyVerifiedUser()
        
        await self.session.execute(update(User).where(User.email == user_email).values(is_verified = True))
        await self.session.commit()
        await self.cache.delete(f"verification_token:{user_email}")

    async def login(self, email: str, password: str) -> dict:
        result = await self.session.execute(select(User).where(User.email == email))
        user: User = result.scalars().first()

        if not user or not verify_password(password, user.password):
            raise InvalidCredentials()

        if not user.is_verified:
            token_value = await self.cache.get(f"verification_token:{email}")
            if not token_value:
                await self._send_verification_email(email)
            raise UserNotVerified()

        access_token = create_token({"sub": email}, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_token({"sub": email}, settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        return {"access_token":access_token,
                "refresh_token": refresh_token}

        
    
    async def _send_verification_email(self, email: str):
        verification_token = create_token({"sub": email}, settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)
        await self.cache.set(f"verification_token:{email}", 
                verification_token, 
                ex=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES*60)
        await self.email_service.send_message("Email confirmation", f"""To verify your email follow the link: \n
                                        {settings.DOMAIN}/auth/verify/{verification_token}""", 
                                        email)
