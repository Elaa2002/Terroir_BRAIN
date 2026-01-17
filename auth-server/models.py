# models.py
"""
Complete database models for the full-featured authentication system.
Uses SQLAlchemy declarative base for User, UserSession, and RevokedToken models.
Includes all required fields: roles, email verification, lockout, session tracking.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base  # Assumes your existing Base from database.py

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", index=True)  # user, admin, etc.
    email_verified = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    lockout_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    revoked_tokens = relationship("RevokedToken", back_populates="user")

    __table_args__ = (
        Index('ix_users_email_verified', 'email_verified'),
    )

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)  # JWT Token ID
    access_jti = Column(String, nullable=True)  # Associated access token JTI
    refresh_jti = Column(String, nullable=True)  # Associated refresh token JTI
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="sessions")

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    token_type = Column(String, nullable=False)  # 'access' or 'refresh'
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="revoked_tokens")
