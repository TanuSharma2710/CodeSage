from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from db.session import get_db
from schemas.auth import TokenData
from schemas.analysis import (
    RecurringErrorsResponse,
    ErrorFrequencyResponse,
    ErrorByLanguageResponse,
    DebugSessionDetail,
    ErrorHistoryResponse,
    ErrorTypeBreakdownResponse,
    SessionErrorCountsResponse
)
from services.analysis_service import (
    get_recurring_errors,
    get_daily_error_frequency,
    get_error_by_language,
    get_debug_session_detail,
    get_error_history,
    get_error_type_breakdown,
    get_session_error_counts
)
from utils.security import get_current_user

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/recurring-errors", response_model=RecurringErrorsResponse)
def recurring_errors(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to look back"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get top recurring errors for the current user in the past N days.
    Returns errors sorted by count in descending order.
    """
    return get_recurring_errors(db, current_user.id, days)


@router.get("/daily-errors", response_model=ErrorFrequencyResponse)
def daily_errors(
    days: int = Query(default=30, ge=7, le=365, description="Number of days to fetch"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily error counts for the error frequency graph.
    Each day includes a color based on error count:
    - 0-4: green
    - 4-8: yellow
    - 8-12: orange
    - 12+: red
    """
    return get_daily_error_frequency(db, current_user.id, days)


@router.get("/error-by-language", response_model=ErrorByLanguageResponse)
def error_by_language(
    error_type: str = Query(..., description="Error type to filter by"),
    error_name: Optional[str] = Query(None, description="Specific error name"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get distribution of a specific error type across different programming languages.
    Used for the language bar chart when an error is selected.
    """
    return get_error_by_language(db, current_user.id, error_type, error_name)


@router.get("/debug-session/{session_id}", response_model=DebugSessionDetail)
def debug_session_detail(
    session_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full details of a debug session for prefilling the debugger.
    Only returns sessions belonging to the current user.
    """
    session = get_debug_session_detail(db, current_user.id, session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debug session not found"
        )
    
    return session


@router.get("/error-history", response_model=ErrorHistoryResponse)
def error_history(
    limit: int = Query(default=10, ge=1, le=50, description="Number of recent errors to fetch"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent error history for the current user.
    Returns errors from latest to oldest with specific error names.
    """
    return get_error_history(db, current_user.id, limit)


@router.get("/error-type-breakdown", response_model=ErrorTypeBreakdownResponse)
def error_type_breakdown(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get breakdown of errors by type (syntax, runtime, logical, etc.)
    from the daily_analysis table for the bar chart.
    """
    return get_error_type_breakdown(db, current_user.id)


@router.get("/session-error-counts/{session_id}", response_model=SessionErrorCountsResponse)
def session_error_counts(
    session_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get error counts by type from a specific debug session.
    Returns the actual counts stored in the session's error count columns.
    """
    result = get_session_error_counts(db, current_user.id, session_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debug session not found"
        )
    
    return result

