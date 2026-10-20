"""
Notification endpoints for users
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.notification import Notification, NotificationList
from app.services.notification_service import NotificationService
from app.services.database import get_database
from app.core.security import get_current_active_user, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("/", response_model=NotificationList)
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get notifications for the current user"""
    notification_service = NotificationService(db)
    
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.user_id,
        skip=skip,
        limit=limit
    )
    
    unread_count = await notification_service.get_unread_count(current_user.user_id)
    total = await notification_service.collection.count_documents({"user_id": current_user.user_id})
    
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count
    }

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark a notification as read"""
    notification_service = NotificationService(db)
    
    success = await notification_service.mark_as_read(notification_id, current_user.user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark all notifications as read for the current user"""
    notification_service = NotificationService(db)
    
    count = await notification_service.mark_all_as_read(current_user.user_id)
    
    return {
        "message": f"{count} notification(s) marked as read",
        "count": count
    }

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a notification"""
    notification_service = NotificationService(db)
    
    success = await notification_service.delete_notification(notification_id, current_user.user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted successfully"}

@router.get("/unread-count")
async def get_unread_count(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get count of unread notifications"""
    notification_service = NotificationService(db)
    
    count = await notification_service.get_unread_count(current_user.user_id)
    
    return {"unread_count": count}

