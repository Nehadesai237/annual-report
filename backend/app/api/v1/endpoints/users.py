"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.models.user import User, UserUpdate, UserRole, UserProfile
from app.services.user_service import UserService
from app.services.database import get_database
from app.core.security import get_current_active_user, require_admin, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user profile"""
    user_service = UserService(db)
    user = await user_service.get_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update current user profile"""
    user_service = UserService(db)
    
    # Check if user exists
    user = await user_service.get_by_id(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    updated_user = await user_service.update_user(current_user.user_id, user_update)
    return updated_user

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    department: str = None,
    role: UserRole = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all users (admin only)"""
    user_service = UserService(db)
    users = await user_service.get_users(
        skip=skip,
        limit=limit,
        department=department,
        role=role
    )
    return users

@router.get("/all-students")
async def get_all_students(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all students (excluding admins) for group member selection"""
    from bson import ObjectId
    from datetime import datetime
    
    # Query database directly to avoid User model validation issues
    users_collection = db.users
    
    # Build filter for students (excluding admins and current user)
    # Don't filter by is_active - get all students like admin panel does
    filter_dict = {
        "role": UserRole.STUDENT.value,
        "_id": {"$ne": ObjectId(current_user.user_id)}  # Exclude current user
    }
    
    # Query database directly
    cursor = users_collection.find(filter_dict).limit(1000)
    
    # Convert to profile format with email included
    profiles = []
    async for user_doc in cursor:
        try:
            # Skip current user (double check)
            if str(user_doc["_id"]) == current_user.user_id:
                continue
            
            # Skip admins (double check)
            if user_doc.get("role") != UserRole.STUDENT.value:
                continue
            
            # Get created_at, default to current time if missing
            created_at = user_doc.get("created_at")
            if not created_at:
                created_at = datetime.utcnow()
            
            # Create profile dict with email included (even though UserProfile model doesn't have it)
            # We'll return a dict instead of UserProfile to include email
            profile = {
                "id": str(user_doc["_id"]),
                "_id": str(user_doc["_id"]),  # Include both for compatibility
                "name": user_doc.get("name", "Unknown"),
                "email": user_doc.get("email", ""),  # Include email for search
                "department": user_doc.get("department", ""),
                "role": user_doc.get("role", "student"),
                "student_id": user_doc.get("student_id"),
                "year_of_study": user_doc.get("year_of_study"),
                "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at
            }
            profiles.append(profile)
        except Exception as e:
            # Log error but continue with other users
            print(f"Error creating profile for user {user_doc.get('_id')}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    return profiles

@router.get("/search", response_model=List[UserProfile])
async def search_users(
    q: str = Query(..., description="Search query (name or email)"),
    limit: int = 20,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Search users by name or email"""
    user_service = UserService(db)
    
    # Search users by name or email
    users = await user_service.search_users(query=q, limit=limit)
    
    # Convert to profile format
    profiles = []
    for user in users:
        try:
            # UserProfile expects _id as the alias for id
            profile = UserProfile(
                _id=user.id,  # Use _id alias as expected by UserProfile
                name=user.name,
                department=user.department or "",
                role=user.role,
                student_id=user.student_id,
                year_of_study=user.year_of_study,
                created_at=user.created_at
            )
            profiles.append(profile)
        except Exception as e:
            # Log error but continue with other users
            print(f"Error creating profile for user {user.id}: {e}")
            continue
    
    return profiles

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get user by ID"""
    user_service = UserService(db)
    
    # Users can only view their own profile unless they're admin
    if current_user.user_id != user_id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user (admin only)"""
    user_service = UserService(db)
    
    # Check if user exists
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    updated_user = await user_service.update_user(user_id, user_update)
    return updated_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete user (admin only)"""
    user_service = UserService(db)
    
    # Check if user exists
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot delete self
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Delete user
    await user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}

@router.get("/department/{department}/users", response_model=List[User])
async def get_users_by_department(
    department: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get users by department"""
    user_service = UserService(db)
    
    # Users can only view users from their own department unless they're admin
    if (current_user.role != UserRole.ADMIN.value and 
        current_user.department != department):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view users from other departments"
        )
    
    users = await user_service.get_users_by_department(department)
    return users