from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    email: EmailStr | None = None

class UserBase(BaseModel):
    username: str | None = None
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str  # Plain text password from user

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        return v


class UserCreateGoogle(BaseModel):
    """Schema for Google OAuth user creation"""
    google_id: str
    email: EmailStr
    email_verified: bool = False
    
    @field_validator('google_id')
    @classmethod
    def validate_google_id(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError('Invalid Google ID')
        return v

class UserResponse(UserBase):
    """Schema for user responses (what API returns)"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserPermissions(BaseModel):
    can_scrape: bool
    can_view_analytics: bool
    can_manage_users: bool

class UserMeResponse(BaseModel):
    """Minimal user data for frontend display"""
    username: str | None
    email: EmailStr
    full_name: str | None
    permissions: UserPermissions


class PasswordChangeRequest(BaseModel):
    current: str
    new: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

class DeleteAccountRequest(BaseModel):
    password: str


    
