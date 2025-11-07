from datetime import datetime, timedelta, timezone
import os
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from src.settings import settings
from src.auth.crud import get_user_by_username, get_user_by_email, update_password
from src.auth.password_service import password_service
from src.database.models import User
import resend
import re
from typing import Literal

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    to_encode.update({'sub': str(data.get("sub"))})

    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    return encoded_jwt

def authenticate_user(identifier: str, password: str,  db: Session ) -> User | None:
    """Authenticate user with username and password"""

    login_type = detect_login_type(identifier)

    if login_type == "username":
        user = get_user_by_username(identifier, db)
    else:
        user = get_user_by_email(identifier, db)

    if not user or not user.is_active:
        return None
    if not password_service.verify_password(password, user.hashed_password):
        return None
    return user


def detect_login_type(identifier: str) -> Literal["email", "username"]:
    """Detect if identifier is an email or username."""
    # Simple email pattern check
    print('identifier in the detect login type', identifier)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return "email" if re.match(email_pattern, identifier) else "username"

def create_password_reset_token(email: str, db: Session) -> dict:
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {
            "success": True, 
            "message": "If an account exists, a reset email has been sent"
        }
    
    # Create JWT token
    payload = {
        "user_id": user.id,
        "exp": datetime.now() + timedelta(hours=1),
        "type": "password_reset"
    }
    
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    reset_link = f"{settings.frontend_url}/reset-password?token={token}"
    resend.api_key = settings.resend_api_key
    try:
        params = {
            "from": os.getenv("EMAIL_FROM", "onboarding@resend.dev"),
            "to": [email],
            "subject": "Reset Your Password",
            "html": f"""
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
            """
        }
        
        result = resend.Emails.send(params)
        print('✅ Email sent successfully! Result:', result)
        return {"success": True, "message": "If an account exists, a reset email has been sent"}
    
    except Exception as e:
        print('❌ ERROR SENDING EMAIL:')
        print(f'Error type: {type(e).__name__}')
        print(f'Error message: {str(e)}')
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Failed to send reset email: {str(e)}"}

def reset_password_with_token(token: str, new_password: str, db: Session) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        if payload.get("type") != "password_reset":
            return {"success": False, "message": "Invalid token"}
        
        user_id = payload.get("user_id")
        hased_password = password_service.hash_password(new_password)
        user = update_password(user_id, hased_password, db)
        if not user:
            return {"success": False, "message": "User not found"}

        return {"success": True, "message": "Password reset successfully"}
        
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Invalid token"}




