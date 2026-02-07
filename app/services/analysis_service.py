from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional
from models.debug_session import DebugSession, DailyAnalysis
from schemas.analysis import (
    RecurringErrorItem,
    RecurringErrorsResponse,
    DailyErrorCount,
    ErrorFrequencyResponse,
    LanguageErrorCount,
    ErrorByLanguageResponse,
    DebugSessionDetail,
    ErrorHistoryItem,
    ErrorHistoryResponse,
    ErrorTypeCount,
    ErrorTypeBreakdownResponse,
    SessionErrorCountsResponse
)


def get_error_color(count: int) -> str:
    """Get color based on error count."""
    if count <= 4:
        return "green"
    elif count <= 8:
        return "yellow"
    elif count <= 12:
        return "orange"
    else:
        return "red"


def get_recurring_errors(db: Session, user_id: int, days: int = 7) -> RecurringErrorsResponse:
    """
    Get top recurring errors for a user in the past N days.
    Uses the DailyAnalysis table which stores aggregated error counts by type.
    Returns errors sorted by count in descending order.
    """
    start_date = date.today() - timedelta(days=days)
    end_date = date.today()
    
    # Query to aggregate error counts by type from DailyAnalysis table
    daily_records = (
        db.query(
            func.sum(DailyAnalysis.syntax_error_count).label('syntax_count'),
            func.sum(DailyAnalysis.runtime_error_count).label('runtime_count'),
            func.sum(DailyAnalysis.logical_error_count).label('logical_count'),
            func.sum(DailyAnalysis.type_error_count).label('type_count'),
            func.sum(DailyAnalysis.import_error_count).label('import_count'),
            func.sum(DailyAnalysis.other_error_count).label('other_count'),
            func.max(DailyAnalysis.date).label('last_date')
        )
        .filter(
            DailyAnalysis.user_id == user_id,
            DailyAnalysis.date >= start_date,
            DailyAnalysis.date <= end_date
        )
        .first()
    )
    
    # Build list of error types with their counts
    error_types = []
    if daily_records:
        error_mapping = [
            ('Syntax Error', 'SyntaxError', daily_records.syntax_count or 0),
            ('Runtime Error', 'RuntimeError', daily_records.runtime_count or 0),
            ('Logical Error', 'LogicalError', daily_records.logical_count or 0),
            ('Type Error', 'TypeError', daily_records.type_count or 0),
            ('Import Error', 'ImportError', daily_records.import_count or 0),
            ('Other Error', 'OtherError', daily_records.other_count or 0),
        ]
        
        for error_name, error_type, count in error_mapping:
            if count > 0:
                # Get the most recent debug session for this error type
                # Map error type to the appropriate count column
                error_type_lower = error_type.lower().replace("error", "")
                
                # Build query based on error type count column
                if 'syntax' in error_type_lower:
                    filter_cond = DebugSession.syntax_error_count > 0
                elif 'runtime' in error_type_lower:
                    filter_cond = DebugSession.runtime_error_count > 0
                elif 'logical' in error_type_lower:
                    filter_cond = DebugSession.logical_error_count > 0
                elif 'type' in error_type_lower:
                    filter_cond = DebugSession.type_error_count > 0
                elif 'import' in error_type_lower:
                    filter_cond = DebugSession.import_error_count > 0
                else:
                    filter_cond = DebugSession.other_error_count > 0
                
                recent_session = (
                    db.query(DebugSession.id, DebugSession.created_at)
                    .filter(
                        DebugSession.user_id == user_id,
                        filter_cond
                    )
                    .order_by(desc(DebugSession.created_at))
                    .first()
                )
                
                error_types.append({
                    'error_name': error_name,
                    'error_type': error_type,
                    'count': count,
                    'last_occurred': recent_session.created_at if recent_session else datetime.now(timezone.utc),
                    'debug_session_id': recent_session.id if recent_session else None
                })
    
    # Sort by count descending
    error_types.sort(key=lambda x: x['count'], reverse=True)
    
    errors = []
    total = 0
    for err in error_types:
        errors.append(RecurringErrorItem(
            error_type=err['error_type'],
            error_name=err['error_name'],
            count=err['count'],
            last_occurred=err['last_occurred'],
            debug_session_id=err['debug_session_id']
        ))
        total += err['count']
    
    return RecurringErrorsResponse(
        errors=errors,
        total_count=total,
        period_days=days
    )


def get_daily_error_frequency(
    db: Session, 
    user_id: int, 
    days: int = 30
) -> ErrorFrequencyResponse:
    """
    Get daily error counts for the past N days for the graph.
    Uses DailyAnalysis table which stores the actual error count per day.
    Colors are based on dynamic thresholds calculated from mean:
    - Green: 0 to mean/2
    - Yellow: mean/2 to mean
    - Orange: mean to 3*mean/2
    - Red: above 3*mean/2
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Query daily counts from DailyAnalysis table (has actual error count per day)
    daily_counts_query = (
        db.query(
            DailyAnalysis.date,
            DailyAnalysis.total_error_count
        )
        .filter(
            DailyAnalysis.user_id == user_id,
            DailyAnalysis.date >= start_date,
            DailyAnalysis.date <= end_date
        )
        .all()
    )
    
    # Create a dict of existing counts from DailyAnalysis
    counts_dict = {row.date: row.total_error_count for row in daily_counts_query}
    
    # Calculate total errors and mean
    total_errors = sum(counts_dict.values())
    mean = total_errors / days if days > 0 else 0
    
    # Calculate dynamic thresholds based on mean
    # If mean is 0, use default thresholds of 1, 2, 3
    if mean == 0:
        green_max = 1
        yellow_max = 2
        orange_max = 3
    else:
        green_max = mean / 2
        yellow_max = mean
        orange_max = (3 * mean) / 2
    
    def get_dynamic_color(count: int) -> str:
        """Get color based on dynamic thresholds."""
        if count <= green_max:
            return "green"
        elif count <= yellow_max:
            return "yellow"
        elif count <= orange_max:
            return "orange"
        else:
            return "red"
    
    # Fill in all days, including zeros
    daily_counts = []
    current = start_date
    while current <= end_date:
        count = counts_dict.get(current, 0)
        daily_counts.append(DailyErrorCount(
            date=current,
            count=count,
            color=get_dynamic_color(count)
        ))
        current += timedelta(days=1)
    
    return ErrorFrequencyResponse(
        daily_counts=daily_counts,
        start_date=start_date,
        end_date=end_date,
        total_errors=total_errors,
        mean=round(mean, 2),
        green_max=round(green_max, 2),
        yellow_max=round(yellow_max, 2),
        orange_max=round(orange_max, 2)
    )


def get_error_by_language(
    db: Session, 
    user_id: int, 
    error_type: str,
    error_name: Optional[str] = None
) -> ErrorByLanguageResponse:
    """
    Get distribution of a specific error type across different languages.
    """
    # Determine the right filter based on error_type
    error_type_lower = error_type.lower()
    if 'syntax' in error_type_lower:
        filter_cond = DebugSession.syntax_error_count > 0
    elif 'runtime' in error_type_lower:
        filter_cond = DebugSession.runtime_error_count > 0
    elif 'logical' in error_type_lower or 'logic' in error_type_lower:
        filter_cond = DebugSession.logical_error_count > 0
    elif 'type' in error_type_lower:
        filter_cond = DebugSession.type_error_count > 0
    elif 'import' in error_type_lower:
        filter_cond = DebugSession.import_error_count > 0
    else:
        filter_cond = DebugSession.other_error_count > 0
    
    query = db.query(
        DebugSession.language,
        func.count(DebugSession.id).label('count')
    ).filter(
        DebugSession.user_id == user_id,
        filter_cond
    )
    
    if error_name:
        query = query.filter(DebugSession.error_name == error_name)
    
    results = query.group_by(DebugSession.language).order_by(desc('count')).all()
    
    languages = []
    total = 0
    for row in results:
        languages.append(LanguageErrorCount(
            language=row.language or "unknown",
            count=row.count
        ))
        total += row.count
    
    return ErrorByLanguageResponse(
        error_type=error_type,
        error_name=error_name,
        languages=languages,
        total_count=total
    )


def get_debug_session_detail(
    db: Session, 
    user_id: int, 
    session_id: int
) -> Optional[DebugSessionDetail]:
    """
    Get full details of a debug session for prefilling the debugger.
    Only returns if the session belongs to the user.
    """
    session = db.query(DebugSession).filter(
        DebugSession.id == session_id,
        DebugSession.user_id == user_id
    ).first()
    
    if not session:
        return None
    
    # Derive error_type from the count columns
    if session.syntax_error_count > 0:
        error_type = 'syntax'
    elif session.runtime_error_count > 0:
        error_type = 'runtime'
    elif session.logical_error_count > 0:
        error_type = 'logical'
    elif session.type_error_count > 0:
        error_type = 'type'
    elif session.import_error_count > 0:
        error_type = 'import'
    else:
        error_type = 'other'
    
    return DebugSessionDetail(
        id=session.id,
        code=session.code,
        error_message=session.error_message,
        error_type=error_type,
        error_name=session.error_name,
        wrong_lines=session.wrong_lines,
        corrected_lines=session.corrected_lines,
        language=session.language,
        diagnosis=session.diagnosis,
        fixed_code=session.fixed_code,
        study_topics=session.study_topics,
        created_at=session.created_at
    )


def update_daily_analysis(db: Session, user_id: int, error_type: str, count: int = 1) -> None:
    """
    Update the daily analysis stats when a new debug session is created.
    Called after each debug session is saved.
    
    Args:
        count: Number of mistakes found (default 1)
    """
    today = date.today()
    print(f"[DEBUG] update_daily_analysis: user_id={user_id}, error_type={error_type}, count={count}, date={today}")
    
    # Try to get existing record for today
    daily_record = db.query(DailyAnalysis).filter(
        DailyAnalysis.user_id == user_id,
        DailyAnalysis.date == today
    ).first()
    
    if not daily_record:
        # Create new record for today
        print(f"[DEBUG] Creating new DailyAnalysis record for user_id={user_id}, date={today}")
        daily_record = DailyAnalysis(
            user_id=user_id,
            date=today,
            syntax_error_count=0,
            runtime_error_count=0,
            logical_error_count=0,
            type_error_count=0,
            import_error_count=0,
            other_error_count=0,
            total_error_count=0
        )
        db.add(daily_record)
    else:
        print(f"[DEBUG] Found existing DailyAnalysis record, current total={daily_record.total_error_count}")
    
    # Increment the appropriate counter by the count
    # Use consistent substring matching with debugger_service.py
    error_type_lower = error_type.lower()
    if 'syntax' in error_type_lower or 'indentation' in error_type_lower:
        daily_record.syntax_error_count += count
    elif 'type' in error_type_lower and 'import' not in error_type_lower:
        # Check for "type" but exclude "import" to avoid false positives
        daily_record.type_error_count += count
    elif 'import' in error_type_lower or 'module' in error_type_lower:
        daily_record.import_error_count += count
    elif 'runtime' in error_type_lower or 'name' in error_type_lower or 'index' in error_type_lower or 'key' in error_type_lower or 'value' in error_type_lower or 'attribute' in error_type_lower or 'zerodivision' in error_type_lower:
        daily_record.runtime_error_count += count
    elif 'logic' in error_type_lower:
        daily_record.logical_error_count += count
    else:
        daily_record.other_error_count += count
    
    daily_record.total_error_count += count
    db.commit()
    print(f"[DEBUG] DailyAnalysis updated: new total_error_count={daily_record.total_error_count}")


def get_error_history(
    db: Session,
    user_id: int,
    limit: int = 10
) -> ErrorHistoryResponse:
    """
    Get recent debug sessions for a user, ordered from latest to oldest.
    Returns error_name (specific like "IndexError - List index out of bounds").
    """
    sessions = (
        db.query(DebugSession)
        .filter(DebugSession.user_id == user_id)
        .order_by(desc(DebugSession.created_at))
        .limit(limit)
        .all()
    )
    
    # Get total count
    total = db.query(func.count(DebugSession.id)).filter(
        DebugSession.user_id == user_id
    ).scalar()
    
    errors = []
    for session in sessions:
        # Derive error_type from the count columns
        if session.syntax_error_count > 0:
            error_type = 'syntax'
        elif session.runtime_error_count > 0:
            error_type = 'runtime'
        elif session.logical_error_count > 0:
            error_type = 'logical'
        elif session.type_error_count > 0:
            error_type = 'type'
        elif session.import_error_count > 0:
            error_type = 'import'
        else:
            error_type = 'other'
        
        errors.append(ErrorHistoryItem(
            id=session.id,
            error_name=session.error_name,
            error_type=error_type,
            language=session.language or "python",
            created_at=session.created_at
        ))
    
    return ErrorHistoryResponse(
        errors=errors,
        total_count=total or 0
    )


def get_error_type_breakdown(
    db: Session,
    user_id: int
) -> ErrorTypeBreakdownResponse:
    """
    Get total error counts by type from daily_analysis table.
    Returns breakdown of syntax, runtime, logical, type, import, and other errors.
    """
    # Sum all error counts by type across all days for this user
    result = (
        db.query(
            func.sum(DailyAnalysis.syntax_error_count).label('syntax'),
            func.sum(DailyAnalysis.runtime_error_count).label('runtime'),
            func.sum(DailyAnalysis.logical_error_count).label('logical'),
            func.sum(DailyAnalysis.type_error_count).label('type'),
            func.sum(DailyAnalysis.import_error_count).label('import'),
            func.sum(DailyAnalysis.other_error_count).label('other')
        )
        .filter(DailyAnalysis.user_id == user_id)
        .first()
    )
    
    error_types = []
    total = 0
    
    if result:
        type_mapping = [
            ('Syntax Error', result.syntax or 0),
            ('Runtime Error', result.runtime or 0),
            ('Logical Error', result.logical or 0),
            ('Type Error', result.type or 0),
            ('Import Error', result.import_ if hasattr(result, 'import_') else (result[4] or 0)),
            ('Other Error', result.other or 0)
        ]
        
        for error_type, count in type_mapping:
            if count > 0:
                error_types.append(ErrorTypeCount(
                    error_type=error_type,
                    count=count
                ))
                total += count
    
    return ErrorTypeBreakdownResponse(
        error_types=error_types,
        total_count=total
    )


def get_session_error_counts(
    db: Session,
    user_id: int,
    session_id: int
) -> Optional[SessionErrorCountsResponse]:
    """
    Get error counts by type from a specific debug session.
    Returns the actual counts stored in the session's error count columns.
    Only returns if the session belongs to the user.
    """
    session = db.query(DebugSession).filter(
        DebugSession.id == session_id,
        DebugSession.user_id == user_id
    ).first()
    
    if not session:
        return None
    
    total = (
        (session.syntax_error_count or 0) +
        (session.runtime_error_count or 0) +
        (session.logical_error_count or 0) +
        (session.type_error_count or 0) +
        (session.import_error_count or 0) +
        (session.other_error_count or 0)
    )
    
    return SessionErrorCountsResponse(
        session_id=session.id,
        syntax_error_count=session.syntax_error_count or 0,
        runtime_error_count=session.runtime_error_count or 0,
        logical_error_count=session.logical_error_count or 0,
        type_error_count=session.type_error_count or 0,
        import_error_count=session.import_error_count or 0,
        other_error_count=session.other_error_count or 0,
        total_count=total
    )
