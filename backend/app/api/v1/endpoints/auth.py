"""
Simplified Authentication Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any
import traceback

from app.core.config import settings
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_active_user
)
from app.models.user import User, UserCreate, UserLogin, Token, TokenData, UserUpdate, PasswordChange
from app.services.user_service import UserService
from app.services.database import get_database
from app.core.exceptions import AuthenticationError, ValidationError, ConflictError
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


def handle_auth_response(success: bool, data: Any = None, message: str = None) -> Dict[str, Any]:
    """Standardized authentication response"""
    return {
        "success": success,
        "data": data,
        "message": message
    }


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user
    
    Returns:
        User object
    """
    try:
        user_service = UserService(db)
        user = await user_service.create_user(user_data)
        
        return user
        
    except (ValidationError, ConflictError, HTTPException) as e:
        # Re-raise validation, conflict and HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login")
async def login(
    user_credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login user and return access token
    
    Returns:
        Token with user data
    """
    try:
        user_service = UserService(db)
        
        # Authenticate user
        user = await user_service.authenticate_user(
            user_credentials.email, 
            user_credentials.password
        )
        
        # Create access token
        if user_credentials.remember_me:
            access_token_expires = timedelta(days=30)
        else:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
            },
            expires_delta=access_token_expires
        )
        
        token_data = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user
        )
        
        return token_data.model_dump() if hasattr(token_data, 'model_dump') else token_data.dict()
        
    except AuthenticationError as e:
        # AuthenticationError has proper error details
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/login-form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Login using OAuth2 password form (for Swagger UI)"""
    try:
        user_service = UserService(db)
        
        user = await user_service.authenticate_user(
            form_data.username,
            form_data.password
        )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
            },
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user
        )
        
    except AuthenticationError:
        raise


@router.get("/me")
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user information"""
    try:
        user_service = UserService(db)
        user = await user_service.get_by_id(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@router.put("/me")
async def update_current_user(
    user_update: UserUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update current user information"""
    try:
        user_service = UserService(db)
        updated_user = await user_service.update_user(current_user.user_id, user_update)
        return updated_user
        
    except ValidationError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Change user password"""
    try:
        user_service = UserService(db)
        success = await user_service.change_password(current_user.user_id, password_data)
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
            
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/refresh")
async def refresh_token(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Refresh access token"""
    try:
        user_service = UserService(db)
        user = await user_service.get_by_id(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": current_user.user_id,
                "email": current_user.email,
                "role": current_user.role
            },
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: TokenData = Depends(get_current_active_user)
):
    """Logout user"""
    return {"message": "Logged out successfully"}
