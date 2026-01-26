from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate
from app.utils.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from datetime import datetime, timedelta, timezone
from app.config import settings
import secrets


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user in the database."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user.password)
    
    # Create new user
    new_user = User(
        email=user.email,
        password=hashed_password,
        name=user.name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user and return the user object."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    
    return user


def create_user_tokens(db: Session, user: User) -> dict:
    """
    Create access and refresh tokens for the user.
    Refresh token is stored in database for secure rotation.
    Also cleans up expired tokens for this user (serverless-friendly).
    """
    # Clean up expired tokens for this user (prevents database bloat)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    
    # Create access token (stateless, not stored)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token with unique identifier
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    token_id = secrets.token_urlsafe(32)  # Unique token identifier
    refresh_token = create_refresh_token(
        data={"user_id": user.id, "token_id": token_id},
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token in database
    expires_at = datetime.now(timezone.utc) + refresh_token_expires
    db_refresh_token = RefreshToken(
        token=token_id,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """
    Refresh the access token using a valid refresh token.
    
    SECURITY: Each refresh token can only be used ONCE.
    - When used, the old token is DELETED
    - A new token is issued and stored
    """
    # Verify the JWT refresh token
    token_data = verify_refresh_token(refresh_token)
    token_id = token_data.token_id
    user_id = token_data.id
    
    # Find the token in database
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_id,
        RefreshToken.user_id == user_id
    ).first()
    
    # If token not found, it was already used or never existed
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already used refresh token"
        )
    
    # Check if token has expired
    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        # Delete expired token
        db.delete(db_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    
    # Delete the current token (single-use - it's being used now)
    db.delete(db_token)
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = create_access_token(
        data={"user_id": user_id},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token with new unique identifier
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    new_token_id = secrets.token_urlsafe(32)
    new_refresh_token = create_refresh_token(
        data={"user_id": user_id, "token_id": new_token_id},
        expires_delta=refresh_token_expires
    )
    
    # Store new refresh token in database
    expires_at = datetime.now(timezone.utc) + refresh_token_expires
    new_db_token = RefreshToken(
        token=new_token_id,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(new_db_token)
    db.commit()
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


def delete_all_user_tokens(db: Session, user_id: int) -> None:
    """Delete all refresh tokens for a user (used on logout)."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).delete()
    db.commit()


def logout_user(db: Session, user_id: int) -> None:
    """Logout user by deleting all their refresh tokens."""
    delete_all_user_tokens(db, user_id)


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get a user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def cleanup_expired_tokens(db: Session) -> int:
    """
    Delete all expired and revoked refresh tokens from the database.
    
    This should be run periodically (e.g., daily via a cron job or background task)
    to prevent database bloat.
    
    Returns the number of tokens deleted.
    """
    # Delete all revoked tokens
    revoked_count = db.query(RefreshToken).filter(
        RefreshToken.is_revoked == True
    ).delete()
    
    # Delete all expired tokens (even if not revoked)
    expired_count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    
    db.commit()
    
    return revoked_count + expired_count



