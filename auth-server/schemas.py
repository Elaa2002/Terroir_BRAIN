# schemas.py
"""
Complete Pydantic schemas for all authentication endpoints.
Provides input/output validation for register, login, tokens, email verify, 
password reset, sessions, and protected user info.
Supports role-based responses and full FastAPI type hints.
"""

from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from passlib.context import CryptContext  # For type hints only

# ------------------ Core User Schemas ------------------
class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserOut(UserBase):
    id: int
    email_verified: bool
    is_locked: bool
    created_at: datetime
    active_sessions: int = 0  # Computed field
    model_config = {"from_attributes": True} # Use model_config for V2

class UserMe(UserOut):
    """Current user info for /auth/me"""
    pass

# ------------------ Token Schemas ------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenResponse(Token):
    """Response for login/refresh"""
    user: UserOut

class TokenPayload(BaseModel):
    """Internal JWT payload"""
    sub: str  # user_id
    jti: str
    role: Optional[str] = None
    exp: datetime

# ------------------ Email Verification Schemas ------------------
class EmailVerify(BaseModel):
    token: str

class EmailVerifyResponse(BaseModel):
    verified: bool
    message: str

# ------------------ Password Reset Schemas ------------------
class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    password: str = Field(..., min_length=8)
    token: str

class ResetPasswordResponse(BaseModel):
    success: bool
    message: str
    invalidate_sessions: bool = True

# ------------------ Session Management Schemas ------------------
class UserSessionBase(BaseModel):
    jti: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    last_activity: Optional[datetime] = None

class UserSessionCreate(UserSessionBase):
    pass

class UserSessionOut(UserSessionBase):
    id: int
    user_id: int
    is_revoked: bool
    revoked_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True} # Use model_config for V2

class UserSessionsResponse(BaseModel):
    sessions: List[UserSessionOut]
    total: int

class LogoutResponse(BaseModel):
    success: bool
    message: str
    revoked_count: int = 0

# ------------------ Security Schemas ------------------
class Login(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(TokenResponse):
    """Extended response with session info"""
    session_id: Optional[int] = None

# ------------------ HTTP Exception Schemas ------------------
class HTTPError(BaseModel):
    detail: str
    status_code: int

# ------------------ Config for all schemas ------------------
class Config:
    # Enable ORM mode for SQLAlchemy compatibility
    from_attributes = True
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }
# ------------------ Token & Password Schemas ------------------
class TokenRefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class MessageResponse(BaseModel):
    message: str

# auth-server/schemas.py

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    model_config = {"from_attributes": True}