from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import database_service
from src.api.pydantic_models import UserCreate, UserMeResponse, Token, UserPermissions
from src.settings import settings
import src.api.user_services as crud
import src.api.auth_services as auth
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(database_service.get_db)):
    """Register a new user"""
    # Check if username already exists
    db_user = crud.get_user_by_username(username=user.username, db=db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = crud.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = crud.create_user(user=user, db=db)
    return UserMeResponse.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database_service.get_db)
):
    """Login and get access token"""
    
    # Authenticate user
    user = crud.authenticate_user(form_data.username, form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")




def get_user_permissions(user: UserMeResponse) -> UserPermissions:
    """Calculate user permissions based on roles"""
    has_admin_role = any(role.name == "admin" for role in user.roles)
    
    return UserPermissions(
        can_scrape=has_admin_role or user.is_superuser,
        can_view_analytics=True,  # All users can view
        can_manage_users=user.is_superuser,
    )

@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: Annotated[UserMeResponse, Depends(auth.get_current_active_user)]
):
    """Get current authenticated user information"""
    return UserMeResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        permissions=get_user_permissions(current_user)
    )
