from sqlalchemy.orm import Session
from src.database.models import User, Role, user_roles
# from src.api.pydantic_models import UserCreate, UserCreateGoogle
from src.auth.schemas import UserCreate, UserCreateGoogle
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from datetime import datetime, timedelta
import os
from jose import jwt
import resend
import re
from typing import Literal
from src.settings import settings
from sqlalchemy.exc import IntegrityError

class PasswordService:
    """Secure password hashing using Argon2."""
    
    def __init__(self):
        # Configure Argon2 parameters
        # These are secure defaults, but you can adjust based on your needs
        self.ph = PasswordHasher(
            time_cost=2,        # Number of iterations
            memory_cost=65536,  # Memory usage in KiB (64 MB)
            parallelism=4,      # Number of parallel threads
            hash_len=32,        # Length of hash in bytes
            salt_len=16         # Length of random salt in bytes
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2.
        Salt is automatically generated and included in the hash.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string (includes salt and parameters)
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        return self.ph.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed: Previously hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.ph.verify(hashed, password)
            return True
        except VerifyMismatchError:
            # Password doesn't match
            return False
        except (VerificationError, InvalidHash) as e:
            # Invalid hash format or other verification error
            print(f"Password verification error: {e}")
            return False
    
    def needs_rehash(self, hashed: str) -> bool:
        """
        Check if a hash needs to be rehashed with updated parameters.
        Useful if you change security parameters over time.
        """
        try:
            return self.ph.check_needs_rehash(hashed)
        except (InvalidHash, Exception):
            return True


# Create a singleton instance
password_service = PasswordService()

# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password."""
    return password_service.hash_password(password)

def get_user_by_username(username: str, db: Session) -> User | None:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(email: str, db: Session) -> User | None:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: int, db: Session) -> User | None:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_google_id(google_id: str, db: Session) -> User | None:
    """Find user by Google ID"""
    print('type db', type(db))
    print('db', db)
    return db.query(User).filter(User.google_id == google_id).first()

def get_user_roles(user_id: int, db: Session):
    specific_role = db.query(Role).join(
        user_roles, user_roles.c.role_id == Role.id
    ).filter(
        user_roles.c.user_id == user_id
    ).first()

    return specific_role

def create_user(user: UserCreate, db: Session) -> User:
    """Create a new user"""
    # Hash the password
    hashed_password = hash_password(user.password)

    # Create user instance
    db_user = User(
        auth_provider="local",
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    # Assign default 'user' role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e):
            raise ValueError("Username already exists")
        elif "email" in str(e):
            raise ValueError("Email already registered")
        raise

def create_google_user(db: Session, user_in: UserCreateGoogle) -> User:
    """Create a new user from Google OAuth"""
    print('creating google user with', user_in)
    db_user = User(
        auth_provider="google",
        google_id=user_in.google_id,
        email=user_in.email,
        username=None,  # OAuth users don't have usernames
        hashed_password=None,  # OAuth users don't have passwords
        full_name=None,  # Not collecting for now
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e):
            raise ValueError("Email already registered with another account")
        elif "google_id" in str(e):
            raise ValueError("Google account already linked")
        raise


def update_google_user(db: Session, user: User, user_in: UserCreateGoogle) -> User:
    """Update existing Google user (e.g., if email changed)"""
    
    # Update fields that might have changed
    user.email = user_in.email
    user.updated_at = datetime.now()
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e):
            raise ValueError("Email already in use by another account")
        raise


def get_or_create_google_user(
    db: Session, 
    user_in: UserCreateGoogle
) -> tuple[User, bool]:
    """
    Get existing Google user or create new one.
    Returns: (user, created) where created is True if new user was created
    """
    
    # Try to find by Google ID first
    existing_user = get_user_by_google_id( user_in.google_id, db)
    print('existing user found by google id', existing_user)
    if existing_user:
        # Update and return existing user
        updated_user = update_google_user(db, existing_user, user_in)
        return updated_user, False
    print('Not existing user', existing_user)

    # Check if email exists with different auth provider
    email_user = get_user_by_email(user_in.email, db)
    if email_user and email_user.auth_provider == "local":
        raise ValueError(
            "This email is already registered with password login. "
            "Please log in with your password."
        )
    print('Not email_user', email_user)

    # Create new user
    new_user = create_google_user(db, user_in)
    return new_user, True

def update_password(user_id: int, new_hashed_password: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None  # or raise an exception
    
    user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(user)  # Refresh to get updated data
    
    return user

def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None  # or raise an exception
    
    user.is_active = False  # Add this field to your User model
    user.deleted_at = datetime.now()
    db.commit()
    
    return True

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
        hased_password = hash_password(new_password)
        user = update_password(user_id, hased_password, db)
        if not user:
            return {"success": False, "message": "User not found"}

        return {"success": True, "message": "Password reset successfully"}
        
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Invalid token"}