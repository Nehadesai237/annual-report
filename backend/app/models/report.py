"""
Report model and schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class ReportType(str, Enum):
    """Report types enum"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    DEPARTMENT = "department"
    YEARLY = "yearly"

class ReportStatus(str, Enum):
    """Report status enum"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportBase(BaseModel):
    """Base report schema"""
    type: ReportType
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None

class ReportCreate(ReportBase):
    """Report creation schema"""
    params: Dict[str, Any] = {}

class ReportInDB(ReportBase):
    """Report in database schema"""
    id: str = Field(alias="_id")
    generated_by: str
    params: Dict[str, Any]
    status: ReportStatus = ReportStatus.GENERATING
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

class Report(ReportBase):
    """Report response schema"""
    id: str
    generated_by: str
    params: Dict[str, Any]
    status: ReportStatus
    file_path: Optional[str]
    file_size: Optional[int]
    generated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        populate_by_name = True

class ReportFilters(BaseModel):
    """Report filters schema"""
    type: Optional[ReportType] = None
    generated_by: Optional[str] = None
    status: Optional[ReportStatus] = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class ReportStats(BaseModel):
    """Report statistics schema"""
    total_activities: int
    accepted_activities: int
    rejected_activities: int
    pending_activities: int
    total_users: int
    departments: List[Dict[str, Any]]
    activity_types: List[Dict[str, Any]]
    monthly_stats: List[Dict[str, Any]]
