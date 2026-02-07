from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class DebugSession(Base):
    """
    Stores each debugging session with code, error details, and fixes.
    """
    __tablename__ = "debug_sessions"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Code submitted by user
    code = Column(Text, nullable=False)
    
    # Error from terminal
    error_message = Column(Text, nullable=False)
    
    # Error counts by type - stores count of each error type in this session
    syntax_error_count = Column(Integer, default=0)
    runtime_error_count = Column(Integer, default=0)
    logical_error_count = Column(Integer, default=0)
    import_error_count = Column(Integer, default=0)
    type_error_count = Column(Integer, default=0)
    other_error_count = Column(Integer, default=0)
    error_name = Column(String(255))  # 5-10 word summary e.g. "IndexError - List index out of bounds"
    
    # Lines with issues (for diff highlighting)
    changed_line_numbers = Column(Text)  # JSON array of line numbers that were changed [3, 5, 7]
    wrong_lines = Column(Text)  # JSON array of original code snippets
    corrected_lines = Column(Text)  # JSON array of corrected code snippets
    
    # Full fix details
    language = Column(String(50), default="python")
    diagnosis = Column(Text)  # AI explanation of the error
    fixed_code = Column(Text)  # Complete fixed code
    study_topics = Column(Text)  # JSON array of topics to study
    
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship to user
    user = relationship("User", backref="debug_sessions")


class DailyAnalysis(Base):
    """
    Stores daily error statistics per user for the analysis dashboard.
    One row per user per day.
    """
    __tablename__ = "daily_analysis"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Date of the analysis (without time)
    date = Column(Date, nullable=False, index=True)
    
    # Error counts by type
    syntax_error_count = Column(Integer, default=0)
    runtime_error_count = Column(Integer, default=0)
    logical_error_count = Column(Integer, default=0)
    type_error_count = Column(Integer, default=0)
    import_error_count = Column(Integer, default=0)
    other_error_count = Column(Integer, default=0)
    
    # Total errors for the day
    total_error_count = Column(Integer, default=0)
    
    # Ensure one row per user per day
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )

    # Relationship to user
    user = relationship("User", backref="daily_analysis")


class ErrorTracking(Base):
    """
    Tracks recurring errors for the 'Top Recurring Errors' feature.
    """
    __tablename__ = "error_tracking"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    error_type = Column(String(100), nullable=False)
    error_name = Column(String(255))  # Summary of the error
    error_count = Column(Integer, default=1)
    last_occurred = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship to user
    user = relationship("User", backref="error_tracking")

