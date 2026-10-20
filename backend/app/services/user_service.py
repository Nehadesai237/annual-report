"""
User service for database operations with enhanced security
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User, UserCreate, UserUpdate, UserInDB, UserRole, PasswordChange, UserProfile
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException, status
from app.core.exceptions import AuthenticationError, ValidationError, ConflictError

class UserService:
    """User service for database operations with enhanced security"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with enhanced validation"""
        # Check if user already exists
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError("Email already exists. Please use a different email or try logging in.")
        
        # Check if student ID already exists (for students)
        if user_data.role == UserRole.STUDENT and user_data.student_id:
            existing_student = await self.collection.find_one({"student_id": user_data.student_id})
            if existing_student:
                raise ConflictError("Student ID already exists")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "department": user_data.department,
            "role": user_data.role.value,
            "student_id": user_data.student_id,
            "phone": user_data.phone,
            "year_of_study": user_data.year_of_study,
            "is_active": True,
            "email_verified": False,
            "last_login": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        
        return UserInDB(**user_doc)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return None
            
            user_doc["_id"] = str(user_doc["_id"])
            # Remove sensitive fields
            user_doc.pop("password_hash", None)
            user_doc.pop("login_attempts", None)
            user_doc.pop("locked_until", None)
            
            return User(**user_doc)
        except Exception:
            return None
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email (includes sensitive fields for authentication)"""
        user_doc = await self.collection.find_one({"email": email})
        if not user_doc:
            return None
        
        user_doc["_id"] = str(user_doc["_id"])
        return UserInDB(**user_doc)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await self.get_by_email(email)
        if not user:
            raise AuthenticationError("No account found with this email address. Please check your email or register.")
        
        # Check if account is active (default to True if not set)
        is_active = getattr(user, 'is_active', True)
        if not is_active:
            raise AuthenticationError("Your account has been deactivated. Please contact the administrator.")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Incorrect password. Please try again or reset your password.")
        
        # Update last login
        await self.collection.update_one(
            {"_id": ObjectId(user.id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Get fresh user data without sensitive fields
        user_doc = await self.collection.find_one({"_id": ObjectId(user.id)})
        if not user_doc:
            return None
            
        user_doc["_id"] = str(user_doc["_id"])
        # Remove sensitive fields
        user_doc.pop("password_hash", None)
        user_doc.pop("login_attempts", None)
        user_doc.pop("locked_until", None)
        
        return User(**user_doc)
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update user with validation"""
        # Check if student ID already exists (for students)
        if user_update.student_id:
            existing_student = await self.collection.find_one({
                "student_id": user_update.student_id,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing_student:
                raise ValidationError("Student ID already exists")
        
        # Prepare update data
        update_data = {}
        if user_update.name is not None:
            update_data["name"] = user_update.name
        if user_update.department is not None:
            update_data["department"] = user_update.department
        if user_update.role is not None:
            update_data["role"] = user_update.role.value
        if user_update.student_id is not None:
            update_data["student_id"] = user_update.student_id
        if user_update.phone is not None:
            update_data["phone"] = user_update.phone
        if user_update.year_of_study is not None:
            update_data["year_of_study"] = user_update.year_of_study
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise ValidationError("User not found")
        
        # Return updated user
        return await self.get_by_id(user_id)
    
    async def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """Change user password with security checks"""
        user = await self.get_by_email((await self.get_by_id(user_id)).email)
        if not user:
            raise ValidationError("User not found")
        
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = get_password_hash(password_data.new_password)
        
        # Update password
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return True
    
    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user (deactivate instead of hard delete)"""
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.matched_count > 0
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        department: Optional[str] = None,
        role: Optional[UserRole] = None,
        active_only: bool = True
    ) -> List[User]:
        """Get users with filters"""
        # Build filter
        filter_dict = {}
        if department:
            filter_dict["department"] = department
        if role:
            filter_dict["role"] = role.value
        if active_only:
            filter_dict["is_active"] = True
        
        # Get users
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        users = []
        
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            # Remove sensitive fields
            user_doc.pop("password_hash", None)
            user_doc.pop("login_attempts", None)
            user_doc.pop("locked_until", None)
            users.append(User(**user_doc))
        
        return users
    
    async def get_users_by_department(self, department: str) -> List[User]:
        """Get users by department"""
        cursor = self.collection.find({"department": department, "is_active": True})
        users = []
        
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            # Remove sensitive fields
            user_doc.pop("password_hash", None)
            user_doc.pop("login_attempts", None)
            user_doc.pop("locked_until", None)
            users.append(User(**user_doc))
        
        return users
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by name or email"""
        # Create regex pattern for case-insensitive search
        search_pattern = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
                {"student_id": {"$regex": query, "$options": "i"}}
            ],
            "is_active": True
        }
        
        cursor = self.collection.find(search_pattern).limit(limit)
        users = []
        
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            # Remove sensitive fields
            user_doc.pop("password_hash", None)
            user_doc.pop("login_attempts", None)
            user_doc.pop("locked_until", None)
            users.append(User(**user_doc))
        
        return users
    
    async def get_user_count(self) -> int:
        """Get total active user count"""
        return await self.collection.count_documents({"is_active": True})
    
    async def get_department_stats(self) -> List[dict]:
        """Get statistics by department"""
        pipeline = [
            {"$match": {"is_active": True}},
            {
                "$group": {
                    "_id": "$department",
                    "count": {"$sum": 1},
                    "roles": {"$addToSet": "$role"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        stats = []
        async for doc in self.collection.aggregate(pipeline):
            stats.append({
                "department": doc["_id"],
                "count": doc["count"],
                "roles": doc["roles"]
            })
        
        return stats
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile for public display"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        return UserProfile(
            id=user.id,
            name=user.name,
            department=user.department,
            role=user.role,
            student_id=user.student_id,
            year_of_study=user.year_of_study,
            created_at=user.created_at
        )
