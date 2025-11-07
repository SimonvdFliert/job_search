from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from src.database import database_service
from src.auth.schemas import Token, UserCreate, UserCreateGoogle, UserResponse, UserPermissions, UserMeResponse, PasswordChangeRequest, ForgotPasswordRequest, PasswordResetRequest, DeleteAccountRequest
from src.settings import settings
from src.auth.password_service import password_service
import src.auth.auth_services as auth_service
import src.auth.crud as auth_crud
import src.auth.deps as auth_deps
from authlib.integrations.starlette_client import OAuth
import os

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=settings.secret_key,
    redirect_uri=settings.google_redirect_uri,
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(database_service.get_db)):
    """Register a new user"""
    db_user = auth_crud.get_user_by_username(username=user.username, db=db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    db_user = auth_crud.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = auth_crud.create_user(user=user, db=db)
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database_service.get_db)
):
    """Login and get access token"""
    
    user = auth_service.authenticate_user(form_data.username, form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")



@router.post("/change_password")
async def change_password(
    current_user: Annotated[UserResponse, Depends(auth_deps.get_current_active_user)],
    password_data: PasswordChangeRequest,
    db: Session = Depends(database_service.get_db)
):
    all_user_details = auth_crud.get_user_by_id(current_user.id, db=db)

    current_hashed_password = all_user_details.hashed_password

    current_passwords_match = password_service.verify_password(password=password_data.current, 
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
    
    new_hashed_password = password_service.hash_password(password_data.new)
    auth_crud.update_password( 
        user_id=current_user.id, 
        new_hashed_password=new_hashed_password,
        db=db
    )

    return {"message": "Password changed successfully"}


@router.post("/forgot_password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(database_service.get_db)
):
    """Request a password reset email"""
    result = auth_service.create_password_reset_token(request.email, db)
    return {"message": result["message"]}

@router.post("/reset_password")
async def change_password(
    request: PasswordResetRequest,
    db: Session = Depends(database_service.get_db)
):
    result = auth_service.reset_password_with_token(
        token=request.token,
        new_password=request.new_password,
        db=db
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}

@router.post("/delete_account")
async def delete_account(
    delete_data: DeleteAccountRequest,
    current_user: Annotated[UserResponse, Depends(auth_deps.get_current_active_user)],
    db: Session = Depends(database_service.get_db)
):
    print('delete data', delete_data)
    user = auth_crud.get_user_by_id(current_user.id, db=db)
    if not password_service.verify_password(delete_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    auth_crud.delete_user(user_id=current_user.id, db=db)
    return {"message": "Account deleted successfully"}



def get_user_permissions(user: UserResponse, db: Session ) -> UserPermissions:
    """Calculate user permissions based on roles"""

    try:    
        user_roles = auth_crud.get_user_roles(user.id, db=db)

        if user_roles and user_roles.name == "admin":
            has_admin_role = True
        else:
            has_admin_role = False
    except:
        has_admin_role = False
    
    return UserPermissions(
        can_scrape=has_admin_role or user.is_superuser,
        can_view_analytics=True,
        can_manage_users=user.is_superuser,
    )

@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(auth_deps.get_current_active_user)],
    db: Session = Depends(database_service.get_db)
):
    """Get current authenticated user information"""
    return UserMeResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        permissions=get_user_permissions(current_user, db)
    )


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.google_redirect_uri
    response = await oauth.google.authorize_redirect(request, redirect_uri)   
    return response

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(database_service.get_db)):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        google_user = UserCreateGoogle(
            google_id=user_info.get("sub"),
            email=user_info.get("email"),
            email_verified=user_info.get("email_verified", False),
        )
        
        user, is_new = auth_crud.get_or_create_google_user(db, google_user)
        
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
        redirect_path = "/auth/callback"
        
        return RedirectResponse(
            f"{frontend_url}{redirect_path}?token={access_token}&new_user={str(is_new).lower()}"
        )
        
    except ValueError as e:
        frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
        return RedirectResponse(
            f"{frontend_url}/login?error={str(e)}"
        )
    except Exception as e:
        print(f"OAuth error: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
        return RedirectResponse(
            f"{frontend_url}/login?error=authentication_failed"
        )