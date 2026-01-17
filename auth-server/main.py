# auth-server/main.py

"""
Complete FastAPI application for Auth Server (Port 8001).
Includes Gmail SMTP integration and Pydantic V2 compatibility.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Added Credentials for Logout
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic_settings import BaseSettings
from pydantic import EmailStr, SecretStr

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Local imports
from database import get_db, engine, Base
from models import User, UserSession, RevokedToken

# Updated schemas to include all endpoints from your Insomnia list
from schemas import (
    UserCreate, UserOut, TokenResponse, Token, Login, EmailVerify, 
    ForgotPassword, ResetPassword, ResetPasswordResponse, UserMe, 
    UserSessionsResponse, LogoutResponse, UserSessionOut,
    TokenRefreshRequest, ForgotPasswordRequest, ResetPasswordRequest # <--- CHECK THIS
)
# Updated auth utilities to include the 'revoke_all' logic
from auth import (
    create_access_token, create_refresh_token, create_email_verify_token,
    create_password_reset_token, verify_token, get_password_hash, verify_password,
    get_current_user, require_role, check_lockout, increment_lockout,
    revoke_user_sessions, create_user_session, revoke_token, is_token_revoked,
    revoke_all_user_tokens, security, SECRET_KEY, ALGORITHM  # Added security and keys
)

# If you haven't moved your mailer to a separate file, 
# ensure you define send_password_reset_email here as well.
# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "1234567890abcdef1234567890abcdef")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# --- Email Configuration ---
# Note: We use SecretStr for Pydantic V2 compatibility with fastapi-mail
mail_conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your-email@gmail.com"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-app-password"),
    MAIL_FROM = os.getenv("MAIL_FROM", "your-email@gmail.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Terroir Auth Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# --- Email Helper Function ---
async def send_verification_email(email: str, token: str):
    # CRITICAL: Verify this matches the @app.get route exactly
    # If testing via Insomnia/Browser on your host machine, localhost:8001 is correct
    verification_url = f"http://localhost:8001/auth/verify-email?token={token}"
    
    html = f"""
    <div style="font-family: sans-serif; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <h2>Verify your email</h2>
        <p>Thanks for signing up! Please click the link below to verify your account:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" style="background: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Account</a>
        </div>
        <p>Or copy and paste this link:</p>
        <p style="font-size: 0.8em; color: #666;">{verification_url}</p>
        <p style="margin-top: 20px; font-size: 0.8em; color: #666;">If you didn't request this, ignore this email.</p>
    </div>
    """
    
    message = MessageSchema(
        subject="Terroir Auth - Verify Your Email",
        recipients=[email],
        body=html,
        subtype="html"
    )

    fm = FastMail(mail_conf)
    await fm.send_message(message)

# ------------------ Endpoints ------------------

@app.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        email_verified=False  # Ensure they start unverified
    )
    
    try:
        # 3. Commit to DB FIRST to avoid 500 errors if DB fails after email sent
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 4. Generate Token and Send Email
        verify_token_str = create_email_verify_token(db_user.email)
        await send_verification_email(db_user.email, verify_token_str)
        
    except Exception as e:
        db.rollback()
        # Log the specific error for debugging
        print(f"Registration Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    
    # 5. Return tokens so the UI can auto-login or redirect
    access_token = create_access_token({"sub": str(db_user.id), "role": db_user.role})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserOut.model_validate(db_user)
    )

@app.get("/auth/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        # Decode using the same SECRET_KEY and ALGORITHM as auth.py
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")
            
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        if user.email_verified:
            return {"message": "Email already verified. You can login."}
            
        user.email_verified = True
        db.commit()
        return {"message": "Email verified successfully. You can now login."}
        
    except JWTError as e:
        print(f"JWT Verification Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@app.post("/auth/login", response_model=TokenResponse)
async def login(form_data: Login, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        if user: 
            increment_lockout(user, db)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox.")
    
    if user.is_locked:
        raise HTTPException(status_code=423, detail="Account locked due to too many attempts.")
    
    # Reset lockout on success
    user.lockout_attempts = 0
    db.commit()
    
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Session Management
    access_payload = verify_token(access_token, db, "access")
    refresh_payload = verify_token(refresh_token, db, "refresh")
    create_user_session(
        user_id=user.id, 
        jti=access_payload["jti"],
        access_jti=access_payload["jti"], 
        refresh_jti=refresh_payload["jti"],
        ip_address=request.client.host, 
        user_agent=request.headers.get("user-agent", ""),
        db=db
    )
    
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token,
        token_type="bearer", 
        user=UserOut.model_validate(user)
    )

@app.get("/auth/me", response_model=UserMe)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserMe.model_validate(current_user)

@app.get("/health")
async def health():
    return {"status": "online", "server": "auth", "port": 8001}



@app.head("/auth/check-token")
@app.get("/auth/check-token")
async def check_token(current_user: User = Depends(get_current_user)):
    return {"status": "valid"}

@app.post("/auth/refresh", response_model=Token)
async def refresh_token(data: TokenRefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(data.refresh_token, db, "refresh")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or user.is_locked:
        raise HTTPException(status_code=401, detail="User unavailable")
        
    new_access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": new_access_token,
        "refresh_token": data.refresh_token, # Usually keep the same refresh token
        "token_type": "bearer"
    }




@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials, db, "access")
    jti = payload.get("jti")
    user_id = payload.get("sub")
    
    revoke_token(jti, "access", user_id, db)
    return {"message": "Successfully logged out"}  

@app.post("/auth/logout-all")
async def logout_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    revoke_all_user_tokens(current_user.id, db)
    return {"message": "Logged out from all devices"}

# auth-server/main.py

@app.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        # For testing, it's easier if we tell you the user wasn't found
        raise HTTPException(status_code=404, detail="User not found")
        
    # Generate the token
    reset_token = create_password_reset_token(user.email)
    
    # RETURN THE DATA TO INSOMNIA
    return {
        "message": "Reset token generated",
        "token": reset_token,
        "debug_link": f"http://localhost:8001/auth/reset-password?token={reset_token}"
    }
@app.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    
    # Optional: Log out of all sessions after password change for security
    revoke_all_user_tokens(user.id, db)
    
    return {"message": "Password updated successfully"}
# Example placement in main.py or your email utility file
async def send_password_reset_email(email: str, token: str):
    reset_link = f"http://localhost:8001/auth/reset-password?token={token}"
    # Adding extra lines and flush=True to force Docker to show it
    print("\n" + "="*50, flush=True)
    print(f"CRITICAL DEBUG: Password reset link for {email}:", flush=True)
    print(f"URL: {reset_link}", flush=True)
    print("="*50 + "\n", flush=True)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)