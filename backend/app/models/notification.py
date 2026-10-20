"""
Notification model and schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

class NotificationType(str, Enum):
    """Notification types enum"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACTIVITY_APPROVED = "activity_approved"
    ACTIVITY_REJECTED = "activity_rejected"
    ACTIVITY_DISCARDED = "activity_discarded"

class NotificationBase(BaseModel):
    """Base notification schema"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: NotificationType = NotificationType.INFO

class NotificationCreate(NotificationBase):
    """Notification creation schema"""
    user_id: str

class NotificationCreateAdmin(NotificationBase):
    """Admin notification creation schema"""
    user_id: Optional[str] = None  # None means broadcast to all users
    target_all_users: bool = False  # If True, send to all users

class NotificationInDB(NotificationBase):
    """Notification in database schema"""
    id: str = Field(alias="_id")
    user_id: str
    read: bool = False
    created_at: datetime
    
    class Config:
        populate_by_name = True

class Notification(NotificationBase):
    """Notification response schema"""
    id: str = Field(alias="_id")
    user_id: Optional[str] = None  # Optional for broadcast notifications
    read: bool
    created_at: datetime
    created_by_admin: Optional[bool] = False
    created_by: Optional[str] = None
    
    class Config:
        populate_by_name = True

class NotificationUpdate(BaseModel):
    """Notification update schema"""
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None  # Accept string, will be validated

class NotificationList(BaseModel):
    """Notification list response schema"""
    notifications: list[Notification]
    total: int
    unread_count: int
