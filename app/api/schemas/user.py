from typing import Self
from enum import StrEnum
from pydantic import BaseModel, EmailStr, model_validator

class RoleEnum(StrEnum):
    admin = 'admin'
    expert = 'expert'
    user = 'user'

class UserBase(BaseModel):
    email: EmailStr
    password: str

class UserRegister(UserBase):
    confirm_password: str

    @model_validator(mode='after')
    def check_password_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    
    role: RoleEnum

class UserLogin(UserBase):
    pass