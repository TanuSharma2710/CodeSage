from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.debugger import (
    DebugRequest, 
    DebugResponse, 
    DebugHistoryResponse,
    DebugSessionResponse
)
from app.schemas.auth import TokenData
from app.utils.security import get_current_user
from app.services.debugger_service import debug_code, debug_code_anonymous, get_debug_history

router = APIRouter(prefix="/debug", tags=["Debugger"])


@router.post("/", response_model=DebugResponse)
async def analyze_code(
    request: DebugRequest,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze code with error and return diagnosis, fixes, and study topics.
    Uses Groq AI for intelligent code analysis.
    """
    try:
        result = await debug_code(db, token_data.id, request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing code: {str(e)}"
        )


@router.get("/history", response_model=DebugHistoryResponse)
def get_history(
    limit: int = 10,
    offset: int = 0,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's debug session history.
    """
    sessions, total = get_debug_history(db, token_data.id, limit, offset)
    
    return DebugHistoryResponse(
        sessions=[
            DebugSessionResponse(
                id=s.id,
                code=s.code,
                error_message=s.error_message,
                language=s.language,
                diagnosis=s.diagnosis,
                fixed_code=s.fixed_code,
                study_topics=s.study_topics,
                created_at=s.created_at
            )
            for s in sessions
        ],
        total=total
    )


@router.post("/anonymous", response_model=DebugResponse)
async def analyze_code_anonymous(request: DebugRequest):
    """
    Analyze code without authentication.
    Uses Groq AI for intelligent code analysis.
    """
    try:
        result = await debug_code_anonymous(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing code: {str(e)}"
        )
