from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import database_service
from src.api.pydantic_models import UserCreate, UserResponse, Token, UserPermissions, UserMeResponse
from src.api import user_services
from src.settings import settings
import src.api.user_services as crud
import src.api.auth_services as auth
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(database_service.get_db)):
    """Register a new user"""
    db_user = crud.get_user_by_username(username=user.username, db=db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    db_user = crud.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = crud.create_user(user=user, db=db)
    return UserResponse.model_validate(new_user)


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


class PasswordChangeRequest(BaseModel):
    current: str
    new: str

@router.post("/change_password")
async def change_password(
    current_user: Annotated[UserResponse, Depends(auth.get_current_active_user)],
    password_data: PasswordChangeRequest,
    db: Session = Depends(database_service.get_db)
):
    all_user_details = crud.get_user_by_id(current_user.id, db=db)

    current_hashed_password = all_user_details.hashed_password

    current_passwords_match = crud.password_service.verify_password(password=password_data.current, 
                                                                    hashed=current_hashed_password)
        
    if not current_passwords_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(password_data.new) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be atleast 8 characters!"
        )
    
    if password_data.current == password_data.new:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    new_hashed_password = crud.password_service.hash_password(password_data.new)
    crud.update_password( 
        user_id=current_user.id, 
        new_hashed_password=new_hashed_password,
        db=db
    )

    return {"message": "Password changed successfully"}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot_password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(database_service.get_db)
):
    """Request a password reset email"""
    result = user_services.create_password_reset_token(request.email, db)
    return {"message": result["message"]}



class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

@router.post("/reset_password")
async def change_password(
    request: PasswordResetRequest,
    db: Session = Depends(database_service.get_db)
):
    result = user_services.reset_password_with_token(
        token=request.token,
        new_password=request.new_password,
        db=db
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}


class DeleteAccountRequest(BaseModel):
    password: str

@router.post("/delete_account")
async def delete_account(
    delete_data: DeleteAccountRequest,
    current_user: Annotated[UserResponse, Depends(auth.get_current_active_user)],
    db: Session = Depends(database_service.get_db)
):
    print('delete data', delete_data)
    user = crud.get_user_by_id(current_user.id, db=db)
    if not crud.password_service.verify_password(delete_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    crud.delete_user(user_id=current_user.id, db=db)
    return {"message": "Account deleted successfully"}



def get_user_permissions(user: UserResponse, db: Session ) -> UserPermissions:
    """Calculate user permissions based on roles"""

    try:    
        user_roles = user_services.get_user_roles(user.id, db=db)
    except:
        has_admin_role = False

    if user_roles.name == "admin":
        has_admin_role = True
    else:
        has_admin_role = False
    
    return UserPermissions(
        can_scrape=has_admin_role or user.is_superuser,
        can_view_analytics=True,
        can_manage_users=user.is_superuser,
    )

@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(auth.get_current_active_user)],
    db: Session = Depends(database_service.get_db)
):
    """Get current authenticated user information"""
    return UserMeResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        permissions=get_user_permissions(current_user, db)
    )


