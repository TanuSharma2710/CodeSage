from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Simple login request - just email and password."""
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    id: Optional[int] = None
    token_type: Optional[str] = None  # 'access' or 'refresh'
    token_id: Optional[str] = None  # Unique identifier for refresh token rotation



