from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base


class RefreshToken(Base):
    """
    Store refresh tokens in database for secure token rotation.
    Each refresh token can only be used ONCE - it is deleted after use.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

