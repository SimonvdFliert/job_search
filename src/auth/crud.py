from sqlalchemy.orm import Session
from src.database.models import User, Role, user_roles
from src.auth.schemas import UserCreate, UserCreateGoogle
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.auth.password_service import hash_password

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
