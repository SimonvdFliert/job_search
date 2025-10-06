from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# User schemas
class UserBase(BaseModel):
    username: str
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

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user responses (what API returns)"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithRoles(UserResponse):
    """User response with role names"""
    roles: list[str] = []