from typing import Annotated

from jwt import ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.settings import settings
from src.database import database_service
from src.auth.schemas import TokenData, UserResponse
import src.auth.crud as auth_crud
# OAuth2 scheme for token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(database_service.get_db)
) -> UserResponse:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:

        payload = jwt.decode(
            token=token, 
            key=settings.secret_key, 
            algorithms=[settings.algorithm]
        )

        print('payload in get current user', payload)

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            print('user_id_str is None')
            raise credentials_exception
        try:
            user_id = int(user_id_str)
        except ValueError:
            print('user_id_str is not a valid integer')
            raise credentials_exception
        
        token_data = TokenData(id=user_id, email=payload.get("email"))

    except JWTError:
        print('JWTError occurred')
        raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")


    user = auth_crud.get_user_by_id(user_id=token_data.id, db=db)
    if user is None:
        print('User not found')
        raise credentials_exception
    
    print(user, 'user in get current user')

    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """Get current active user (not disabled)"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    print('current_user in get current active user', current_user)
    return current_user


def require_admin(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> UserResponse:
    """Dependency that requires admin role"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
