from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
