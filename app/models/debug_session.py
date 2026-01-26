from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class DebugSession(Base):
    __tablename__ = "debug_sessions"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    error_message = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    diagnosis = Column(Text)
    fixed_code = Column(Text)
    study_topics = Column(Text)  # JSON string of topics
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship to user
    user = relationship("User", backref="debug_sessions")


class ErrorTracking(Base):
    __tablename__ = "error_tracking"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    error_type = Column(String(100), nullable=False)
    error_count = Column(Integer, default=1)
    last_occurred = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship to user
    user = relationship("User", backref="error_tracking")
