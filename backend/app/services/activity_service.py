"""
Activity service for database operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.activity import (
    Activity, ActivityCreate, ActivityUpdate, ActivityInDB, 
    ActivityFilters, ActivityList, ActivityStatus, ImageResult, MLVerdict
)
from app.services.ml_service import MLService
from app.services.notification_service import NotificationService
import os
import uuid

class ActivityService:
    """Activity service for database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.activities
        self.ml_service = MLService()
        self.notification_service = NotificationService(db)
    
    def _normalize_activity_doc(self, activity_doc: dict) -> dict:
        """Normalize activity document for Pydantic model"""
        activity_doc["_id"] = str(activity_doc["_id"])
        activity_doc["id"] = str(activity_doc["_id"])
        
        # Ensure optional fields exist with None values
        optional_fields = ["admin_reviewed_at", "admin_reviewed_by", "admin_comments", "ml_checked_at", 
                          "certificate_path", "certificate_validation_result"]
        for field in optional_fields:
            if field not in activity_doc:
                activity_doc[field] = None
        
        # Ensure required fields with defaults exist
        if "images" not in activity_doc:
            activity_doc["images"] = []
        if "has_certificate" not in activity_doc:
            activity_doc["has_certificate"] = False
        if "certificate_validated" not in activity_doc:
            activity_doc["certificate_validated"] = False
        if "achievement_type" not in activity_doc:
            activity_doc["achievement_type"] = "individual"
        if "group_members" not in activity_doc:
            activity_doc["group_members"] = []
        
        return activity_doc
    
    async def create_activity_with_certificate(
        self, 
        activity_data: ActivityCreate, 
        user_id: str,
        files: List,
        certificate_path: Optional[str] = None,
        has_certificate: bool = False,
        certificate_validated: bool = False,
        certificate_validation_result: Optional[Dict[str, Any]] = None
    ) -> Activity:
        """Create a new activity with ML verification"""
        # Get user info
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        
        # Save uploaded files
        image_results = []
        for file in files:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join("uploads", unique_filename)
            
            # Ensure uploads directory exists
            os.makedirs("uploads", exist_ok=True)
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # ML verification
            ml_result = await self.ml_service.verify_image(file_path)
            
            # Store path with leading slash for URL construction
            image_path = f"/uploads/{unique_filename}"
            
            image_result = ImageResult(
                filename=file.filename,
                path=image_path,  # Use URL-friendly path
                verdict=MLVerdict.NORMAL if ml_result["verdict"] == "normal" else MLVerdict.ABNORMAL,
                score=ml_result["score"],
                ml_checked_at=datetime.utcnow()
            )
            image_results.append(image_result)
        
        # Determine activity status based on certificate and ML results
        if has_certificate and certificate_validated:
            # If certificate is validated and matches, accept immediately
            status = ActivityStatus.ACCEPTED
        else:
            # Activities without certificates OR with invalid certificates need admin review
            # Always set to PENDING for admin approval regardless of ML results
            # This ensures ALL achievements without certificates are sent to admin
            status = ActivityStatus.PENDING
        
        # Create activity document
        # Ensure has_certificate is explicitly set (False if no certificate provided)
        final_has_certificate = has_certificate and certificate_path is not None
        
        activity_doc = {
            "user_id": user_id,
            "title": activity_data.title,
            "description": activity_data.description,
            "type": activity_data.type.value,
            "department": user["department"],
            "year": activity_data.year,
            "achievement_type": activity_data.achievement_type,
            "group_members": activity_data.group_members or [],
            "images": [img.dict() for img in image_results],
            "certificate_path": certificate_path,
            "has_certificate": final_has_certificate,
            "certificate_validated": certificate_validated if final_has_certificate else False,
            "certificate_validation_result": certificate_validation_result if final_has_certificate else None,
            "status": status.value,
            "ml_checked_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert activity
        result = await self.collection.insert_one(activity_doc)
        activity_doc["_id"] = str(result.inserted_id)
        activity_doc["id"] = str(result.inserted_id)
        
        # Add admin fields if not present (they're optional but required by model)
        if "admin_reviewed_at" not in activity_doc:
            activity_doc["admin_reviewed_at"] = None
        if "admin_reviewed_by" not in activity_doc:
            activity_doc["admin_reviewed_by"] = None
        if "admin_comments" not in activity_doc:
            activity_doc["admin_comments"] = None
        
        # Create notification based on status
        if status == ActivityStatus.ACCEPTED:
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Activity Accepted",
                message=f"Your activity '{activity_data.title}' has been accepted." + 
                       (" Your certificate was validated successfully." if final_has_certificate else ""),
                type="activity_approved"
            )
        elif status == ActivityStatus.PENDING:
            # Create appropriate notification message based on certificate status
            if final_has_certificate:
                message = f"Your activity '{activity_data.title}' is pending admin review. Your certificate will be verified."
            else:
                message = f"Your activity '{activity_data.title}' is pending admin review. Admin will review your submission."
            
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Activity Pending Review",
                message=message,
                type="info"
            )
        
        return Activity(**self._normalize_activity_doc(activity_doc))
    
    async def get_by_id(self, activity_id: str) -> Optional[Activity]:
        """Get activity by ID"""
        try:
            activity_doc = await self.collection.find_one({"_id": ObjectId(activity_id)})
            if not activity_doc:
                print(f"[ActivityService] Activity {activity_id} not found in database")
                return None
            
            return Activity(**self._normalize_activity_doc(activity_doc))
        except Exception as e:
            print(f"[ActivityService] Error getting activity {activity_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_activities(self, filters: ActivityFilters, include_public: bool = False) -> ActivityList:
        """Get activities with filters - includes public admin-created activities if requested"""
        # Build filter dict
        filter_dict = {}
        
        # Only include filters that have values
        user_id_filter = None
        if filters.user_id:
            user_id_filter = filters.user_id
            # Don't add user_id to filter_dict yet - we'll handle it specially for group members
        if filters.department:
            filter_dict["department"] = filters.department
        if filters.type is not None:
            filter_dict["type"] = filters.type.value
        if filters.status is not None:
            filter_dict["status"] = filters.status.value
        if filters.year:
            filter_dict["year"] = filters.year
        
        # If user_id is provided, include activities where user is creator OR group member
        if user_id_filter:
            # Build filter for user's own activities OR group activities where user is a member
            user_activities_filter = {"user_id": user_id_filter}
            for key, value in filter_dict.items():
                user_activities_filter[key] = value
            
            # Build filter for group activities where user is a member
            group_activities_filter = {
                "achievement_type": "group",
                "group_members": user_id_filter
            }
            for key, value in filter_dict.items():
                group_activities_filter[key] = value
            
            # Combine with $or
            filter_dict = {"$or": [user_activities_filter, group_activities_filter]}
        
        # If including public activities, modify the query to include admin-created public activities
        if include_public:
            # Build filter for public admin activities
            public_filter = {"is_public": True, "is_admin_created": True, "status": "accepted"}
            # Copy other filters (except $or) to public filter
            base_filters = {k: v for k, v in filter_dict.items() if k != "$or"}
            public_filter.update(base_filters)
            
            # If we already have an $or filter (from user_id/group_members), add public to it
            if "$or" in filter_dict:
                filter_dict["$or"].append(public_filter)
            else:
                # If no $or exists, create one with the current filter and public filter
                if user_id_filter:
                    filter_dict = {"$or": [filter_dict, public_filter]}
                else:
                    filter_dict = public_filter
        
        # Calculate pagination
        skip = (filters.page - 1) * filters.size
        
        # Get total count
        total = await self.collection.count_documents(filter_dict)
        
        # Get activities
        cursor = self.collection.find(filter_dict).skip(skip).limit(filters.size).sort("created_at", -1)
        activities = []
        
        async for activity_doc in cursor:
            activities.append(Activity(**self._normalize_activity_doc(activity_doc)))
        
        return ActivityList(
            activities=activities,
            total=total,
            page=filters.page,
            size=filters.size,
            pages=(total + filters.size - 1) // filters.size
        )
    
    async def update_activity(self, activity_id: str, activity_update: ActivityUpdate) -> Activity:
        """Update activity"""
        # Prepare update data
        update_data = {}
        if activity_update.title is not None:
            update_data["title"] = activity_update.title
        if activity_update.description is not None:
            update_data["description"] = activity_update.description
        if activity_update.type is not None:
            update_data["type"] = activity_update.type.value
        if activity_update.year is not None:
            update_data["year"] = activity_update.year
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update activity
        result = await self.collection.update_one(
            {"_id": ObjectId(activity_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise ValueError("Activity not found")
        
        # Return updated activity
        return await self.get_by_id(activity_id)
    
    async def delete_activity(self, activity_id: str) -> bool:
        """Delete activity"""
        # Get activity to delete associated files
        activity = await self.get_by_id(activity_id)
        if activity:
            # Delete associated image files
            for image in activity.images:
                # Convert URL path to file system path if needed
                image_path = image.path
                if image_path and image_path.startswith('/uploads/'):
                    # Remove leading slash to get file system path
                    image_path = image_path.lstrip('/')
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
        
        result = await self.collection.delete_one({"_id": ObjectId(activity_id)})
        return result.deleted_count > 0
    
    async def get_user_activities(self, user_id: str) -> List[Activity]:
        """Get activities for a specific user"""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        activities = []
        
        async for activity_doc in cursor:
            activities.append(Activity(**self._normalize_activity_doc(activity_doc)))
        
        return activities
    
    async def get_department_activities(self, department: str) -> List[Activity]:
        """Get activities for a specific department"""
        cursor = self.collection.find({"department": department}).sort("created_at", -1)
        activities = []
        
        async for activity_doc in cursor:
            activities.append(Activity(**self._normalize_activity_doc(activity_doc)))
        
        return activities
    
    async def get_rejected_activities(self) -> List[Activity]:
        """Get all rejected activities"""
        cursor = self.collection.find({"status": ActivityStatus.REJECTED.value}).sort("created_at", -1)
        activities = []
        
        async for activity_doc in cursor:
            activities.append(Activity(**self._normalize_activity_doc(activity_doc)))
        
        return activities
    
    async def get_pending_activities(self) -> List[Activity]:
        """Get all pending activities"""
        cursor = self.collection.find({"status": ActivityStatus.PENDING.value}).sort("created_at", -1)
        activities = []
        
        async for activity_doc in cursor:
            activities.append(Activity(**self._normalize_activity_doc(activity_doc)))
        
        return activities
    
    async def approve_activity(
        self, 
        activity_id: str, 
        admin_user_id: str, 
        comments: Optional[str] = None
    ) -> bool:
        """Approve a rejected activity"""
        update_data = {
            "status": ActivityStatus.ACCEPTED.value,
            "admin_reviewed_at": datetime.utcnow(),
            "admin_reviewed_by": admin_user_id,
            "admin_comments": comments,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": ObjectId(activity_id)},
            {"$set": update_data}
        )
        
        if result.matched_count > 0:
            # Create notification
            activity = await self.get_by_id(activity_id)
            if activity:
                await self.notification_service.create_notification(
                    user_id=activity.user_id,
                    title="Activity Approved",
                    message=f"Your activity '{activity.title}' has been approved by admin.",
                    type="activity_approved"
                )
        
        return result.matched_count > 0
    
    async def discard_activity(
        self, 
        activity_id: str, 
        admin_user_id: str, 
        comments: Optional[str] = None
    ) -> bool:
        """Permanently discard a rejected activity"""
        # Get activity to delete associated files
        activity = await self.get_by_id(activity_id)
        if activity:
            # Delete associated image files
            for image in activity.images:
                # Convert URL path to file system path if needed
                image_path = image.path
                if image_path and image_path.startswith('/uploads/'):
                    # Remove leading slash to get file system path
                    image_path = image_path.lstrip('/')
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
        
        result = await self.collection.delete_one({"_id": ObjectId(activity_id)})
        
        if result.deleted_count > 0:
            # Create notification
            if activity:
                await self.notification_service.create_notification(
                    user_id=activity.user_id,
                    title="Activity Discarded",
                    message=f"Your activity '{activity.title}' has been permanently discarded.",
                    type="activity_discarded"
                )
        
        return result.deleted_count > 0
    
    async def get_admin_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        # Get activity counts by status
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.collection.aggregate(pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        # Get department stats
        dept_pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "count": {"$sum": 1},
                    "accepted": {
                        "$sum": {"$cond": [{"$eq": ["$status", "accepted"]}, 1, 0]}
                    }
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        department_stats = []
        async for doc in self.collection.aggregate(dept_pipeline):
            department_stats.append({
                "department": doc["_id"],
                "total": doc["count"],
                "accepted": doc["accepted"],
                "rejected": doc["count"] - doc["accepted"]
            })
        
        # Get activity type stats
        type_pipeline = [
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        type_stats = []
        async for doc in self.collection.aggregate(type_pipeline):
            type_stats.append({
                "type": doc["_id"],
                "count": doc["count"]
            })
        
        return {
            "total_activities": sum(status_counts.values()),
            "accepted_activities": status_counts.get("accepted", 0),
            "rejected_activities": status_counts.get("rejected", 0),
            "pending_activities": status_counts.get("pending", 0),
            "department_stats": department_stats,
            "type_stats": type_stats
        }
    
    async def get_audit_logs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        cursor = self.db.audit_logs.find().skip(skip).limit(limit).sort("created_at", -1)
        logs = []
        
        async for log_doc in cursor:
            log_doc["_id"] = str(log_doc["_id"])
            logs.append(log_doc)
        
        return logs
