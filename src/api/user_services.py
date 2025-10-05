from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.database.models import User, Role
from src.api.pydantic_models import UserCreate
from fastapi import Depends
from src.database import database_service
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def get_user_by_username(username: str, db: Session = Depends(database_service.get_db)) -> User | None:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(email: str, db: Session = Depends(database_service.get_db)) -> User | None:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(user_id: int, db: Session = Depends(database_service.get_db)) -> User | None:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(user: UserCreate, db: Session = Depends(database_service.get_db)) -> User:
    """Create a new user"""
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create user instance
    db_user = User(
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
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(username: str, password: str,  db: Session = Depends(database_service.get_db)) -> User | None:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user