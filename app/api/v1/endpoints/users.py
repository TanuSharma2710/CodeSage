from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import UserResponse
from schemas.auth import TokenData
from utils.security import get_current_user
from services.auth_service import get_user_by_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current authenticated user's information."""
    user = get_user_by_id(db, token_data.id)
    return user
