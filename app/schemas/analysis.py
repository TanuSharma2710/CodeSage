from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class RecurringErrorItem(BaseModel):
    """A single recurring error entry."""
    error_type: str
    error_name: str
    count: int
    last_occurred: datetime
    debug_session_id: int  # For "Study Now" button to load this session


class RecurringErrorsResponse(BaseModel):
    """Top recurring errors list."""
    errors: List[RecurringErrorItem]
    total_count: int
    period_days: int = 7


class DailyErrorCount(BaseModel):
    """Error count for a single day."""
    date: date
    count: int
    color: str  # 'green', 'yellow', 'orange', 'red' based on dynamic mean


class ErrorFrequencyResponse(BaseModel):
    """Daily error counts for the graph."""
    daily_counts: List[DailyErrorCount]
    start_date: date
    end_date: date
    total_errors: int  # Total errors in the period
    mean: float  # Mean errors per day
    # Dynamic thresholds based on mean
    green_max: float  # 0 to green_max
    yellow_max: float  # green_max to yellow_max
    orange_max: float  # yellow_max to orange_max
    # red is anything above orange_max


class LanguageErrorCount(BaseModel):
    """Error count for a specific language."""
    language: str
    count: int


class ErrorByLanguageResponse(BaseModel):
    """Distribution of a specific error across languages."""
    error_type: str
    error_name: Optional[str]
    languages: List[LanguageErrorCount]
    total_count: int


class DebugSessionDetail(BaseModel):
    """Full debug session for prefilling debugger."""
    id: int
    code: str
    error_message: str
    error_type: str
    error_name: Optional[str]
    wrong_lines: Optional[str]
    corrected_lines: Optional[str]
    language: str
    diagnosis: Optional[str]
    fixed_code: Optional[str]
    study_topics: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorHistoryItem(BaseModel):
    """A single error from user's debug history."""
    id: int
    error_name: Optional[str]  # Specific error like "IndexError - List index out of bounds"
    error_type: str
    language: str
    created_at: datetime


class ErrorHistoryResponse(BaseModel):
    """List of recent errors from latest to oldest."""
    errors: List[ErrorHistoryItem]
    total_count: int


class ErrorTypeCount(BaseModel):
    """Error count for a specific error type."""
    error_type: str
    count: int


class ErrorTypeBreakdownResponse(BaseModel):
    """Breakdown of errors by type from daily_analysis."""
    error_types: List[ErrorTypeCount]
    total_count: int


class SessionErrorCountsResponse(BaseModel):
    """Error counts for a specific debug session."""
    session_id: int
    syntax_error_count: int
    runtime_error_count: int
    logical_error_count: int
    type_error_count: int
    import_error_count: int
    other_error_count: int
    total_count: int


