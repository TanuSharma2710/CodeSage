from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.study import (
    StudyRecommendationRequest,
    StudyRecommendationResponse
)
from schemas.auth import TokenData
from utils.security import get_current_user
from services.study_service import get_study_recommendations

router = APIRouter(prefix="/study", tags=["Study"])


@router.post("/recommendations", response_model=StudyRecommendationResponse)
def get_recommendations(
    request: StudyRecommendationRequest,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get study recommendations for given topics.
    Returns top 5 resources, top 5 YouTube videos, and best video summary.
    """
    return get_study_recommendations(request.topics, request.language)


# Anonymous endpoint for non-logged in users
@router.post("/recommendations/anonymous", response_model=StudyRecommendationResponse)
def get_recommendations_anonymous(request: StudyRecommendationRequest):
    """
    Get study recommendations without authentication.
    """
    return get_study_recommendations(request.topics, request.language)
