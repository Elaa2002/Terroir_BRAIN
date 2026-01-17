# auth.py
"""
Complete authentication utilities and business logic.
Handles JWT creation/validation, password hashing, token revocation, 
email verification tokens, password reset, session management.
Production-ready with secure defaults and database integration.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserSession, RevokedToken
import os 
# ------------------ Security Config ------------------
SECRET_KEY = os.getenv("SECRET_KEY", "123456789azertyuiopqsdfghjklmwxcvbn")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
EMAIL_VERIFY_EXPIRE_HOURS = 24
PASSWORD_RESET_EXPIRE_HOURS = 1
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ------------------ JWT Utilities ------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create minimal access token with JTI and role"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create refresh token (longer lived, no role)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_email_verify_token(email: str) -> str:
    """Short-lived token for email verification"""
    return jwt.encode(
        {"sub": email, "exp": datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFY_EXPIRE_HOURS)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def create_password_reset_token(email: str) -> str:
    """Very short-lived token for password reset"""
    return jwt.encode(
        {"sub": email, "exp": datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_EXPIRE_HOURS)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# auth-server/auth.py

def verify_token(token: str, db: Session, token_type: str = "access") -> Dict[str, Any]:
    """Decode and validate JWT, check revocation"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        jti = payload.get("jti")
        # ADD 'db' HERE:
        if is_token_revoked(jti, token_type, db):
            raise HTTPException(status_code=401, detail="Token revoked")
            
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
# ------------------ Password Utils ------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ------------------ Token/Session Management ------------------
def is_token_revoked(jti: str, token_type: str, db: Session) -> bool:
    """Check if token JTI is in revoked_tokens table"""
    revoked = db.query(RevokedToken).filter(
        RevokedToken.jti == jti,
        RevokedToken.token_type == token_type
    ).first()
    return bool(revoked)

def revoke_token(jti: str, token_type: str, user_id: int, db: Session):
    """Add token to blacklist"""
    if not is_token_revoked(jti, token_type, db):
        revoked = RevokedToken(jti=jti, token_type=token_type, user_id=user_id)
        db.add(revoked)
        db.commit()

def revoke_user_sessions(user_id: int, db: Session , except_jti: Optional[str] = None):
    """Revoke all user sessions/tokens except optional current one"""
    sessions = db.query(UserSession).filter(UserSession.user_id == user_id).all()
    revoked_count = 0
    for session in sessions:
        if except_jti and (session.jti == except_jti or session.access_jti == except_jti or session.refresh_jti == except_jti):
            continue
        session.is_revoked = True
        session.revoked_at = datetime.now(timezone.utc)
        if session.access_jti:
            revoke_token(session.access_jti, "access", user_id, db)
        if session.refresh_jti:
            revoke_token(session.refresh_jti, "refresh", user_id, db)
        revoked_count += 1
    db.commit()
    return revoked_count

# ------------------ Auth Dependencies ------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """JWT dependency - get current user with role"""
    payload = verify_token(credentials.credentials, db, "access")
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_locked:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

def require_role(required_role: str):
    """Role-based dependency"""
    def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail=f"Admin role required")
        return current_user
    return role_checker

# ------------------ Lockout Utils ------------------
def check_lockout(user: User, db: Session) -> bool:
    """Check and update lockout status"""
    if user.is_locked and user.lockout_until > datetime.now(timezone.utc):
        return True
    if user.lockout_until and user.lockout_until <= datetime.now(timezone.utc):
        # Unlock expired attempts
        user.is_locked = False
        user.lockout_attempts = 0
        db.commit()
    return False

def increment_lockout(user: User, db: Session) -> bool:
    """Increment failed attempts, lock if exceeded"""
    user.lockout_attempts += 1
    if user.lockout_attempts >= MAX_LOGIN_ATTEMPTS:
        user.is_locked = True
        user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
    db.commit()
    return user.is_locked

# ------------------ Session Utils ------------------
def create_user_session(user_id: int, db: Session , jti: str, access_jti: str, refresh_jti: str, 
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None
                       ) -> UserSession:
    """Create new session record"""
    session = UserSession(
        user_id=user_id,
        jti=jti,
        access_jti=access_jti,
        refresh_jti=refresh_jti,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
# Add this utility to help with "Logout All"
# auth-server/auth.py

def revoke_all_user_tokens(user_id: int, db: Session):
    """Revokes all active sessions for a specific user"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id, 
        UserSession.is_revoked == False
    ).all()
    
    for session in sessions:
        session.is_revoked = True
        if session.access_jti:
            revoke_token(session.access_jti, "access", user_id, db)
        if session.refresh_jti:
            revoke_token(session.refresh_jti, "refresh", user_id, db)
    db.commit()