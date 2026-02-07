from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json
from models.debug_session import DebugSession, ErrorTracking
from schemas.debugger import DebugRequest, DebugResponse, CodeFix
from services.ai_service import analyze_code


def create_debug_session(
    db: Session, 
    user_id: int, 
    request: DebugRequest,
    ai_result: dict
) -> DebugSession:
    """Create a new debug session and save to database."""
    
    # Extract wrong and corrected lines from fixes
    fixes = ai_result.get("fixes", [])
    wrong_lines = [fix.get("original", "") for fix in fixes]
    corrected_lines = [fix.get("fixed", "") for fix in fixes]
    
    # Get the line numbers that were changed
    changed_line_numbers = ai_result.get("changed_lines", [])
    
    # Count errors by type from each individual fix
    # Each fix now has its own error_type field
    fixes = ai_result.get("fixes", [])
    
    # Initialize all counts to 0
    syntax_error_count = 0
    runtime_error_count = 0
    logical_error_count = 0
    import_error_count = 0
    type_error_count = 0
    other_error_count = 0
    
    def classify_error_type(error_type_str: str) -> str:
        """Classify an error type string into one of the standard categories."""
        et = error_type_str.lower() if error_type_str else "other"
        if "syntax" in et or "indentation" in et:
            return "syntax"
        elif "type" in et and "import" not in et:
            return "type"
        elif "import" in et or "module" in et:
            return "import"
        elif "runtime" in et or "name" in et or "index" in et or "key" in et or "value" in et or "attribute" in et or "zerodivision" in et:
            return "runtime"
        elif "logic" in et:
            return "logical"
        else:
            return "other"
    
    # Count errors from each fix's individual error_type
    for fix in fixes:
        fix_error_type = fix.get("error_type", "")
        category = classify_error_type(fix_error_type)
        
        if category == "syntax":
            syntax_error_count += 1
        elif category == "type":
            type_error_count += 1
        elif category == "import":
            import_error_count += 1
        elif category == "runtime":
            runtime_error_count += 1
        elif category == "logical":
            logical_error_count += 1
        else:
            other_error_count += 1
    
    # Fallback: if no fixes have error_type, use the global error_type
    total_counted = syntax_error_count + runtime_error_count + logical_error_count + import_error_count + type_error_count + other_error_count
    if total_counted == 0:
        # Use the global error_type as fallback
        raw_error_type = ai_result.get("error_type", "unknown").lower()
        mistakes_count = len(ai_result.get("mistakes", [])) or 1
        category = classify_error_type(raw_error_type)
        
        if category == "syntax":
            syntax_error_count = mistakes_count
        elif category == "type":
            type_error_count = mistakes_count
        elif category == "import":
            import_error_count = mistakes_count
        elif category == "runtime":
            runtime_error_count = mistakes_count
        elif category == "logical":
            logical_error_count = mistakes_count
        else:
            other_error_count = mistakes_count
    
    session = DebugSession(
        user_id=user_id,
        code=request.code,
        error_message=request.error_message,
        syntax_error_count=syntax_error_count,
        runtime_error_count=runtime_error_count,
        logical_error_count=logical_error_count,
        import_error_count=import_error_count,
        type_error_count=type_error_count,
        other_error_count=other_error_count,
        error_name=ai_result.get("error_name", ai_result.get("error_type", "Unknown Error")),
        changed_line_numbers=json.dumps(changed_line_numbers),
        wrong_lines=json.dumps(wrong_lines),
        corrected_lines=json.dumps(corrected_lines),
        language=request.language,
        diagnosis=ai_result.get("diagnosis"),
        fixed_code=ai_result.get("fixed_code"),
        study_topics=json.dumps(ai_result.get("study_topics", []))
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def track_error(db: Session, user_id: int, error_type: str, error_name: str = None) -> None:
    """Track error occurrence for user analytics."""
    
    existing = db.query(ErrorTracking).filter(
        ErrorTracking.user_id == user_id,
        ErrorTracking.error_type == error_type
    ).first()
    
    if existing:
        existing.error_count += 1
        existing.last_occurred = func.now()
        if error_name:
            existing.error_name = error_name
    else:
        error_track = ErrorTracking(
            user_id=user_id,
            error_type=error_type,
            error_name=error_name,
            error_count=1
        )
        db.add(error_track)
    
    db.commit()


async def debug_code(db: Session, user_id: int, request: DebugRequest) -> DebugResponse:
    """Analyze code and return debugging results using AI."""
    
    print(f"[DEBUG] debug_code called for user_id={user_id}, language={request.language}")
    
    # Analyze code with AI service (now async with Groq)
    ai_result = await analyze_code(
        code=request.code,
        error_message=request.error_message,
        language=request.language,
        expected_output=request.expected_output
    )
    
    print(f"[DEBUG] AI result received: error_type={ai_result.get('error_type')}, mistakes={len(ai_result.get('mistakes', []))}")
    
    # Save session to database
    session = create_debug_session(db, user_id, request, ai_result)
    print(f"[DEBUG] DebugSession created with id={session.id}")
    
    # Track error for analytics (using the primary/most common error type)
    error_type = ai_result.get("error_type", "unknown")
    error_name = ai_result.get("error_name", error_type)
    track_error(db, user_id, error_type, error_name)
    print(f"[DEBUG] track_error called: user_id={user_id}, error_type={error_type}, error_name={error_name}")
    
    # Update daily analysis for each error type based on the session's counts
    from services.analysis_service import update_daily_analysis
    
    # Call update_daily_analysis for each error type that has a count > 0
    if session.syntax_error_count > 0:
        update_daily_analysis(db, user_id, "syntax", session.syntax_error_count)
        print(f"[DEBUG] update_daily_analysis: syntax_errors={session.syntax_error_count}")
    if session.runtime_error_count > 0:
        update_daily_analysis(db, user_id, "runtime", session.runtime_error_count)
        print(f"[DEBUG] update_daily_analysis: runtime_errors={session.runtime_error_count}")
    if session.logical_error_count > 0:
        update_daily_analysis(db, user_id, "logical", session.logical_error_count)
        print(f"[DEBUG] update_daily_analysis: logical_errors={session.logical_error_count}")
    if session.type_error_count > 0:
        update_daily_analysis(db, user_id, "type", session.type_error_count)
        print(f"[DEBUG] update_daily_analysis: type_errors={session.type_error_count}")
    if session.import_error_count > 0:
        update_daily_analysis(db, user_id, "import", session.import_error_count)
        print(f"[DEBUG] update_daily_analysis: import_errors={session.import_error_count}")
    if session.other_error_count > 0:
        update_daily_analysis(db, user_id, "other", session.other_error_count)
        print(f"[DEBUG] update_daily_analysis: other_errors={session.other_error_count}")
    
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
