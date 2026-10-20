"""
Activity model and schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class ActivityType(str, Enum):
    """Activity types enum"""
    SOCIAL = "social"
    SPORTS = "sports"
    ACADEMIC = "academic"
    CULTURAL = "cultural"
    TECHNICAL = "technical"

class ActivityStatus(str, Enum):
    """Activity status enum"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class MLVerdict(str, Enum):
    """ML verdict enum"""
    NORMAL = "normal"
    ABNORMAL = "abnormal"

class ImageResult(BaseModel):
    """Image verification result"""
    filename: str
    path: str
    verdict: MLVerdict
    score: float
    ml_checked_at: datetime

class ActivityBase(BaseModel):
    """Base activity schema"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    type: ActivityType
    year: int = Field(..., ge=2020, le=2030)
    achievement_type: str = Field(default="individual", description="Type: individual or group")
    group_members: Optional[List[str]] = Field(default=[], description="List of user IDs for group achievements")

class ActivityCreate(ActivityBase):
    """Activity creation schema"""
    pass

class ActivityUpdate(BaseModel):
    """Activity update schema"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    type: Optional[ActivityType] = None
    year: Optional[int] = Field(None, ge=2020, le=2030)

class ActivityInDB(ActivityBase):
    """Activity in database schema"""
    id: str = Field(alias="_id")
    user_id: str
    department: str
    images: List[ImageResult] = []
    certificate_path: Optional[str] = None
    has_certificate: bool = False
    certificate_validated: bool = False
    certificate_validation_result: Optional[Dict[str, Any]] = None
    achievement_type: str = "individual"
    group_members: List[str] = []
    status: ActivityStatus = ActivityStatus.PENDING
    ml_checked_at: Optional[datetime] = None
    admin_reviewed_at: Optional[datetime] = None
    admin_reviewed_by: Optional[str] = None
    admin_comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class Activity(ActivityBase):
    """Activity response schema"""
    id: str
    user_id: str
    department: str
    images: List[ImageResult]
    certificate_path: Optional[str] = None
    has_certificate: bool = False
    certificate_validated: bool = False
    certificate_validation_result: Optional[Dict[str, Any]] = None
    achievement_type: str = "individual"
    group_members: List[str] = []
    status: ActivityStatus
    ml_checked_at: Optional[datetime]
    admin_reviewed_at: Optional[datetime]
    admin_reviewed_by: Optional[str]
    admin_comments: Optional[str]
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None  # Populated from user service for public endpoints
    
    class Config:
        populate_by_name = True

class ActivityList(BaseModel):
    """Activity list response schema"""
    activities: List[Activity]
    total: int
    page: int
    size: int
    pages: int

class ActivityFilters(BaseModel):
    """Activity filters schema"""
    user_id: Optional[str] = None
    department: Optional[str] = None
    type: Optional[ActivityType] = None
    status: Optional[ActivityStatus] = None
    year: Optional[int] = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
