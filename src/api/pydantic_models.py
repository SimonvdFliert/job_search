from pydantic import BaseModel, EmailStr, ConfigDict
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