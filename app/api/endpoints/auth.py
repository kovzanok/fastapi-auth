from typing import Annotated
from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.services.auth import AuthService
from app.api.schemas.user import UserRegister, UserLogin
from app.exceptions.auth import ExpiredToken, InvalidCredentials, UserAlreadyExists, InvalidToken, UserNotFound, AlreadyVerifiedUser, UserNotVerified
from app.dependencies.auth import get_auth_service

auth_router = APIRouter(prefix="/auth", tags=['auth'])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(register_user_data: UserRegister,
                   auth_service: Annotated[AuthService, Depends(get_auth_service)]
                ):
    register_dict = register_user_data.model_dump()
    try:
        await auth_service.register(email=register_dict.get("email"),
                                    password=register_dict.get("password"),
                                    role=register_dict.get("role"))
    except UserAlreadyExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with provided email({register_dict.get("email")}) already exists")
    
    return {"message": "User successfully created"}

@auth_router.get("/verify/{verification_token}")
async def verify_email(verification_token: str, 
                       auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    try:
        await auth_service.verify(verification_token)
    except InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ExpiredToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature expired")
    except AlreadyVerifiedUser:
        return {"message":"Email is already verified"}
    
    return {"message":"Email is verified"}

@auth_router.post("/login")
async def login(login_user_data: UserLogin,
                response: Response, 
                auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    login_dict = login_user_data.model_dump()
    try:
        tokens = await auth_service.login(email=login_dict.get("email"),
                                    password=login_dict.get("password"),)
    except InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    except UserNotVerified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User email is not verified. Check your email for verification")
    
    response.set_cookie("refresh_token", tokens.get("refresh_token"), httponly=True)

    return {"token": tokens.get("access_token")}

    