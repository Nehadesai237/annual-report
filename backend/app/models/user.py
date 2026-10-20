"""
User model and schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId
import re

class UserRole(str, Enum):
    """User roles enum"""
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"

class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address")
    department: str = Field(..., min_length=2, max_length=100, description="Department/Program name")
    role: UserRole = UserRole.STUDENT
    student_id: Optional[str] = Field(None, min_length=3, max_length=20, description="Student ID (for students)")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    year_of_study: Optional[int] = Field(None, ge=1, le=5, description="Year of study (for students)")

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip().title()

    @validator('department')
    def validate_department(cls, v):
        return v.strip().title()

    @validator('student_id')
    def validate_student_id(cls, v):
        if v and not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Student ID must contain only uppercase letters and numbers')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Invalid phone number format')
        return v

class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    student_id: Optional[str] = Field(None, min_length=3, max_length=20)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    year_of_study: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        if v and not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip().title() if v else v

    @validator('department')
    def validate_department(cls, v):
        return v.strip().title() if v else v

    @validator('student_id')
    def validate_student_id(cls, v):
        if v and not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Student ID must contain only uppercase letters and numbers')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Invalid phone number format')
        return v

class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserInDB(UserBase):
    """User in database schema"""
    id: str = Field(alias="_id")
    password_hash: str
    is_active: bool = True
    email_verified: bool = False
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class User(UserBase):
    """User response schema"""
    id: str = Field(alias="_id")
    is_active: bool
    email_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    remember_me: bool = False

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserProfile(BaseModel):
    """User profile for public display"""
    id: str = Field(alias="_id")
    name: str
    department: str
    role: UserRole
    student_id: Optional[str] = None
    year_of_study: Optional[int] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
