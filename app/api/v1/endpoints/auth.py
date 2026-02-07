from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import UserCreate, UserResponse
from schemas.auth import Token, RefreshTokenRequest, TokenData, LoginRequest
from services.auth_service import (
    create_user,
    authenticate_user,
    create_user_tokens,
    refresh_access_token,
    logout_user
)
from utils.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    new_user = create_user(db, user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with email and password to get access and refresh tokens."""
    user = authenticate_user(db, credentials.email, credentials.password)
    tokens = create_user_tokens(db, user)
    return tokens


@router.post("/refresh-token", response_model=Token)
def refresh_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Get new access and refresh tokens using a valid refresh token.
    
    SECURITY: Each refresh token can only be used ONCE.
    If a previously used token is detected, ALL user sessions are terminated.
    """
    tokens = refresh_access_token(db, token_request.refresh_token)
    return tokens


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout the user by revoking all their refresh tokens.
    
    This ensures that even if someone has stolen a refresh token,
    it will become invalid after the user logs out.
    """
    logout_user(db, current_user.id)
    return {"message": "Successfully logged out. All sessions terminated."}




