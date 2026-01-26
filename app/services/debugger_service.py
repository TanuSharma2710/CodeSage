from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json
from app.models.debug_session import DebugSession, ErrorTracking
from app.schemas.debugger import DebugRequest, DebugResponse, CodeFix
from app.services.ai_service import analyze_code


def create_debug_session(
    db: Session, 
    user_id: int, 
    request: DebugRequest,
    ai_result: dict
) -> DebugSession:
    """Create a new debug session and save to database."""
    
    session = DebugSession(
        user_id=user_id,
        code=request.code,
        error_message=request.error_message,
        language=request.language,
        diagnosis=ai_result.get("diagnosis"),
        fixed_code=ai_result.get("fixed_code"),
        study_topics=json.dumps(ai_result.get("study_topics", []))
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def track_error(db: Session, user_id: int, error_type: str) -> None:
    """Track error occurrence for user analytics."""
    
    existing = db.query(ErrorTracking).filter(
        ErrorTracking.user_id == user_id,
        ErrorTracking.error_type == error_type
    ).first()
    
    if existing:
        existing.error_count += 1
        existing.last_occurred = func.now()
    else:
        error_track = ErrorTracking(
            user_id=user_id,
            error_type=error_type,
            error_count=1
        )
        db.add(error_track)
    
    db.commit()


async def debug_code(db: Session, user_id: int, request: DebugRequest) -> DebugResponse:
    """Analyze code and return debugging results using AI."""
    
    # Analyze code with AI service (now async with Groq)
    ai_result = await analyze_code(
        code=request.code,
        error_message=request.error_message,
        language=request.language
    )
    
    # Save session to database
    session = create_debug_session(db, user_id, request, ai_result)
    
    # Track error for analytics
    track_error(db, user_id, ai_result.get("error_type", "UnknownError"))
    
    # Build response
    fixes = [
        CodeFix(
            line_number=fix["line_number"],
            original=fix["original"],
            fixed=fix["fixed"],
            explanation=fix["explanation"]
        )
        for fix in ai_result.get("fixes", [])
    ]
    
    return DebugResponse(
        diagnosis=ai_result["diagnosis"],
        mistakes=ai_result["mistakes"],
        fixes=fixes,
        fixed_code=ai_result["fixed_code"],
        study_topics=ai_result["study_topics"],
        session_id=session.id
    )


async def debug_code_anonymous(request: DebugRequest) -> DebugResponse:
    """Analyze code without user authentication (no database save)."""
    
    # Analyze code with AI service
    ai_result = await analyze_code(
        code=request.code,
        error_message=request.error_message,
        language=request.language
    )
    
    # Build response
    fixes = [
        CodeFix(
            line_number=fix["line_number"],
            original=fix["original"],
            fixed=fix["fixed"],
            explanation=fix["explanation"]
        )
        for fix in ai_result.get("fixes", [])
    ]
    
    return DebugResponse(
        diagnosis=ai_result["diagnosis"],
        mistakes=ai_result["mistakes"],
        fixes=fixes,
        fixed_code=ai_result["fixed_code"],
        changed_lines=ai_result.get("changed_lines", []),
        study_topics=ai_result["study_topics"],
        session_id=None
    )


def get_debug_history(
    db: Session, 
    user_id: int, 
    limit: int = 10,
    offset: int = 0
) -> tuple[List[DebugSession], int]:
    """Get user's debug session history."""
    
    query = db.query(DebugSession).filter(DebugSession.user_id == user_id)
    total = query.count()
    sessions = query.order_by(DebugSession.created_at.desc()).offset(offset).limit(limit).all()
    
    return sessions, total


def get_user_error_stats(db: Session, user_id: int) -> List[ErrorTracking]:
    """Get user's error statistics sorted by count."""
    
    return db.query(ErrorTracking).filter(
        ErrorTracking.user_id == user_id
    ).order_by(ErrorTracking.error_count.desc()).limit(10).all()
